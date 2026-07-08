from flask import Flask, request, jsonify, render_template, send_file
import numpy as np
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

# --- Test Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reaction')
def reaction():
    return render_template('reaction.html')

@app.route('/stroop')
def stroop():
    return render_template('stroop.html')

@app.route('/memory')
def memory():
    return render_template('memory.html')

@app.route('/famous-faces')
def famous_faces():
    return render_template('famous_faces.html')

@app.route('/clock')
def clock():
    return render_template('clock.html')

@app.route('/cookie-theft')
def cookie_theft():
    return render_template('cookie_theft.html')

@app.route('/letter-search')
def letter_search():
    return render_template('letter_search.html')

@app.route('/spiral')
def spiral():
    return render_template('spiral.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/health')
def health():
    return jsonify({'status':'ok'})

# Spiral analysis: expects points list [{x,y,t},...]
def analyze_spiral(points):
    if not points or len(points)<3:
        return {'spiral_score':0, 'notes':'too few points'}
    pts = np.array([[p['x'], p['y'], p.get('t', i*0.01)] for i,p in enumerate(points)])
    xy = pts[:,0:2]
    t = pts[:,2]
    dt = np.diff(t)
    dt[dt==0]=1e-6
    vel = np.linalg.norm(np.diff(xy,axis=0),axis=1)/dt
    if len(vel)==0:
        return {'spiral_score':0}
    jerk = np.mean(np.abs(np.diff(vel))) if len(vel)>1 else 0.0
    vel_std = float(np.std(vel))
    smoothness = 1.0/(1.0+vel_std)
    # deviation from simple polar linear fit
    xc,yc = np.mean(xy,axis=0)
    rel = xy - np.array([xc,yc])
    r = np.linalg.norm(rel,axis=1)
    theta = np.arctan2(rel[:,1], rel[:,0])
    try:
        A = np.vstack([theta, np.ones_like(theta)]).T
        a,b = np.linalg.lstsq(A, r, rcond=None)[0]
        r_fit = a*theta + b
        deviation = float(np.mean(np.abs(r - r_fit)))
    except Exception:
        deviation = float(np.mean(np.abs(r - np.mean(r))))
    dev_norm = np.tanh(deviation/50.0)
    jerk_norm = np.tanh(jerk/100.0)
    raw = (1 - dev_norm)*0.45 + (1 - jerk_norm)*0.35 + smoothness*0.2
    spiral_score = int(np.clip(raw,0,1)*100)
    return {'spiral_score': spiral_score, 'velocity_mean': float(np.mean(vel)), 'jerk': jerk, 'smoothness':smoothness, 'deviation': deviation}

# Main analyze_all endpoint
@app.route('/analyze_all', methods=['POST'])
def analyze_all():
    data = request.json or {}

    # Reaction: list of ms
    rts = data.get('reaction_times', [])
    mean_rt = float(np.mean(rts)) if len(rts)>0 else 1000.0
    # map 150ms -> best(100), 1000ms -> worst(0)
    val = (mean_rt - 150)/(1000-150)
    val = np.clip(val,0,1)
    reaction_score = int((1-val)*100)

    # Stroop: Use Avg RT from correct responses (lower is better)
    stroop_correct = int(data.get('stroop_correct',0))
    stroop_total = int(data.get('stroop_total',0)) or 1
    stroop_avg_rt = float(data.get('stroop_avg_rt', 1000.0))

    # Combine accuracy and RT for Stroop score.
    acc_score = (stroop_correct/stroop_total) * 100
    rt_val = (stroop_avg_rt - 100)/(1000-100)
    rt_val = np.clip(rt_val,0,1)
    rt_score = (1-rt_val) * 100
    stroop_score = int(acc_score * 0.3 + rt_score * 0.7)
    stroop_score = int(np.clip(stroop_score, 0, 100))

    # Memory
    memory_correct = int(data.get('memory_correct',0))
    memory_total = int(data.get('memory_total',1)) or 1
    memory_score = int((memory_correct / memory_total) * 100)

    # Famous faces
    faces_data = data.get('faces', []) if isinstance(data.get('faces', []), list) else []
    face_points = sum(2 if item.get('response') == 'named' else 1 if item.get('response') == 'recognised' else 0 for item in faces_data)
    face_total_points = max(1, len(faces_data) * 2)
    face_score = int((face_points / face_total_points) * 100)

    # Clock drawing
    clock_data = data.get('clock', {}) if isinstance(data.get('clock', {}), dict) else {}
    clock_points = int(clock_data.get('score_points', 0) or 0)
    clock_score = int((clock_points / 6.0) * 100)

    # Cookie theft
    cookie_data = data.get('cookie', {}) if isinstance(data.get('cookie', {}), dict) else {}
    cookie_score = int(cookie_data.get('score', 0) or 0)

    # Letter search
    letter_data = data.get('letter', {}) if isinstance(data.get('letter', {}), dict) else {}
    letter_score = int(letter_data.get('score', 0) or 0)

    # Spiral
    spiral_points = data.get('spiral', {}).get('points', []) if isinstance(data.get('spiral', {}), dict) else data.get('spiral', [])
    spiral_res = analyze_spiral(spiral_points)
    spiral_score = spiral_res.get('spiral_score', 0)

    # Combine with weights
    weights = {
        'reaction':0.125,
        'stroop':0.125,
        'memory':0.125,
        'faces':0.125,
        'spiral':0.125,
        'clock':0.125,
        'cookie':0.125,
        'letter':0.125
    }
    subs = {
        'reaction':reaction_score,
        'stroop':stroop_score,
        'memory':memory_score,
        'faces':face_score,
        'spiral':spiral_score,
        'clock':clock_score,
        'cookie':cookie_score,
        'letter':letter_score
    }
    combined = 0.0
    for k,w in weights.items():
        combined += subs.get(k,0) * w
    risk_index = round(max(0, min(100, 100 - combined)),2)

    out = {
        'user_name': data.get('user_name', 'Participant'),
        'subscores': {
            'Reaction_Time_Score': reaction_score,
            'Stroop_Score': stroop_score,
            'Memory_Score': memory_score,
            'Famous_Faces_Score': face_score,
            'Spiral_Score': spiral_score,
            'Clock_Drawing_Score': clock_score,
            'Cookie_Theft_Score': cookie_score,
            'Letter_Search_Score': letter_score
        },
        'raw_metrics': {
            'Reaction_Avg_ms': round(mean_rt, 2),
            'Stroop_Correct_Ratio': f"{stroop_correct}/{stroop_total}",
            'Stroop_Avg_RT_ms': round(stroop_avg_rt, 2),
            'Memory_Correct_Ratio': f"{memory_correct}/{memory_total}",
            'Famous_Faces_Points': f"{face_points}/{face_total_points}",
            'Clock_Drawing_Points': f"{clock_points}/6",
            'Cookie_Theft_Score': cookie_score,
            'Letter_Search_Score': letter_score
        },
        'spiral_details':spiral_res,
        'risk_index': risk_index
    }
    return jsonify(out)

# Generate PDF report
@app.route('/report', methods=['POST'])
def report():
    payload = request.json or {}
    results = payload.get('results', {})
    name = payload.get('name', 'Participant')

    descriptions = {
        'Reaction_Time_Score': 'Average time to respond. Higher is better (fast response).',
        'Stroop_Score': 'Cognitive flexibility and speed. Higher is better (accurate & fast).',
        'Memory_Score': 'Short-term numerical recall. Higher is better (correct recall).',
        'Famous_Faces_Score': 'Recognition of familiar faces. Higher is better.',
        'Clock_Drawing_Score': 'Planning and organisation of the clock drawing. Higher is better.',
        'Spiral_Score': 'Motor smoothness and tremor. Higher is better (smoother drawing).',
        'Cookie_Theft_Score': 'Visual scene interpretation. Higher is better.',
        'Letter_Search_Score': 'Visual search speed and accuracy. Higher is better.',
        'risk_index': 'Overall screening score (0=Lowest Risk, 100=Highest Risk). Lower is better.'
    }

    tmp = io.BytesIO()
    doc = SimpleDocTemplate(tmp, pagesize=letter, title=f"NEUROTRACK Report for {name}")
    styles = getSampleStyleSheet()
    styleSmall = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8)

    story = [
        Paragraph("<b>NEUROTRACK - Cognitive & Motor Screening Report</b>", styles['Title']),
        Spacer(1,18)
    ]

    story.append(Paragraph(f"<b>Name:</b> {name}", styles['Normal']))
    story.append(Spacer(1,12))

    risk_val = results.get('risk_index', 'N/A')
    story.append(Paragraph(f"<b>Overall Risk Index (0-100): <font color='red'>{risk_val}</font></b>", styles['Heading2']))
    story.append(Paragraph(descriptions['risk_index'], styleSmall))
    story.append(Spacer(1,20))

    story.append(Paragraph("<b>Individual Test Scores (0-100, Higher is Better):</b>", styles['Heading3']))

    if 'subscores' in results and isinstance(results['subscores'], dict):
        for k, v in results['subscores'].items():
            desc = descriptions.get(k, 'Score out of 100.')
            story.append(Paragraph(f"<b>{k.replace('_', ' ')}:</b> {v}", styles['Normal']))
            story.append(Paragraph(f"<i>({desc})</i>", styleSmall))
            story.append(Spacer(1,6))

    story.append(Spacer(1,18))
    story.append(Paragraph("<b>Raw Metrics:</b>", styles['Heading3']))

    if 'raw_metrics' in results and isinstance(results['raw_metrics'], dict):
        for k, v in results['raw_metrics'].items():
            story.append(Paragraph(f"<b>{k.replace('_', ' ')}:</b> {v}", styles['Normal']))
            story.append(Spacer(1,4))

    story.append(Spacer(1,30))
    story.append(Paragraph("<i>Disclaimer: This tool is for informational screening purposes only and is not a medical diagnostic device.</i>", styleSmall))

    doc.build(story)
    tmp.seek(0)

    safe_name = name.replace(' ', '_').replace('.', '').lower() or 'neurotrack_report'
    download_filename = f'neurotrack_Report_{safe_name}.pdf'

    return send_file(tmp, download_name=download_filename, as_attachment=True, mimetype='application/pdf')

# Vercel serverless compatibility
app = app
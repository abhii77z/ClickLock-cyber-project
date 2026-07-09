from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from config import Database
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database
db = Database()

# Helper function to get client IP
def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

# Helper function to update daily stats
def update_daily_stats(stat_type):
    today = datetime.now().date()
    
    # Check if today's record exists
    check_query = "SELECT * FROM defense_stats WHERE date = %s"
    existing = db.fetchone(check_query, (today,))
    
    if existing:
        # Update existing record
        if stat_type == 'click':
            update_query = "UPDATE defense_stats SET total_clicks = total_clicks + 1 WHERE date = %s"
        elif stat_type == 'attack_detected':
            update_query = "UPDATE defense_stats SET attacks_detected = attacks_detected + 1 WHERE date = %s"
        elif stat_type == 'attack_blocked':
            update_query = "UPDATE defense_stats SET attacks_blocked = attacks_blocked + 1 WHERE date = %s"
        db.execute(update_query, (today,))
    else:
        # Create new record
        insert_query = """
            INSERT INTO defense_stats (date, total_clicks, attacks_detected, attacks_blocked, false_positives)
            VALUES (%s, %s, %s, %s, 0)
        """
        values = (today, 1 if stat_type == 'click' else 0, 
                 1 if stat_type == 'attack_detected' else 0,
                 1 if stat_type == 'attack_blocked' else 0)
        db.execute(insert_query, values)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/malicious')
def malicious():
    return render_template('malicious.html')

@app.route('/defender-dashboard')
def defender_dashboard():
    return render_template('defender_dashboard.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query user
        query = "SELECT * FROM admin_users WHERE username = %s"
        user = db.fetchone(query, (username,))
        
        if user and check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# API Routes
@app.route('/api/log-attack', methods=['POST'])
def log_attack():
    try:
        data = request.get_json()
        
        insert_query = """
            INSERT INTO attack_logs 
            (attack_type, target_element, malicious_element, ip_address, user_agent, page_url, blocked, risk_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data.get('attack_type'),
            data.get('target_element'),
            data.get('malicious_element'),
            get_client_ip(),
            request.headers.get('User-Agent'),
            data.get('page_url'),
            data.get('blocked', True),
            data.get('risk_level', 'medium')
        )
        
        db.execute(insert_query, params)
        
        # Update stats
        update_daily_stats('attack_detected')
        if data.get('blocked', True):
            update_daily_stats('attack_blocked')
        
        return jsonify({'success': True, 'message': 'Attack logged'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/log-click', methods=['POST'])
def log_click():
    try:
        data = request.get_json()
        
        insert_query = """
            INSERT INTO legitimate_clicks (element_clicked, page_url, ip_address)
            VALUES (%s, %s, %s)
        """
        
        params = (
            data.get('element'),
            data.get('page_url'),
            get_client_ip()
        )
        
        db.execute(insert_query, params)
        update_daily_stats('click')
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-stats')
def get_stats():
    try:
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        # Today's stats
        today_query = "SELECT * FROM defense_stats WHERE date = %s"
        today_stats = db.fetchone(today_query, (today,))
        
        if not today_stats:
            today_stats = {
                'total_clicks': 0,
                'attacks_detected': 0,
                'attacks_blocked': 0
            }
        
        # Week stats
        week_query = """
            SELECT 
                SUM(total_clicks) as total_clicks,
                SUM(attacks_detected) as attacks_detected,
                SUM(attacks_blocked) as attacks_blocked
            FROM defense_stats 
            WHERE date >= %s
        """
        week_stats = db.fetchone(week_query, (week_ago,))
        
        # All-time stats
        all_query = """
            SELECT 
                SUM(total_clicks) as total_clicks,
                SUM(attacks_detected) as attacks_detected,
                SUM(attacks_blocked) as attacks_blocked
            FROM defense_stats
        """
        all_stats = db.fetchone(all_query)
        
        # Calculate protection rate
        if today_stats['attacks_detected'] > 0:
            protection_rate = (today_stats['attacks_blocked'] / today_stats['attacks_detected']) * 100
        else:
            protection_rate = 100
        
        return jsonify({
            'today': {
                'total_clicks': today_stats['total_clicks'] or 0,
                'attacks_detected': today_stats['attacks_detected'] or 0,
                'attacks_blocked': today_stats['attacks_blocked'] or 0,
                'protection_rate': round(protection_rate, 1)
            },
            'week': {
                'total_clicks': week_stats['total_clicks'] or 0,
                'attacks_detected': week_stats['attacks_detected'] or 0,
                'attacks_blocked': week_stats['attacks_blocked'] or 0
            },
            'all_time': {
                'total_clicks': all_stats['total_clicks'] or 0,
                'attacks_detected': all_stats['attacks_detected'] or 0,
                'attacks_blocked': all_stats['attacks_blocked'] or 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/get-attacks')
def get_attacks():
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        attack_type = request.args.get('attack_type')  # NEW
        offset = (page - 1) * limit

        params = []
        where_clause = ""

        # Apply filter if selected
        if attack_type and attack_type != "ALL":
            where_clause = "WHERE attack_type = %s"
            params.append(attack_type)

        # Get attacks with pagination + filter
        query = f"""
            SELECT * FROM attack_logs
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        attacks = db.fetchall(query, tuple(params))

        # Convert datetime to string
        for attack in attacks:
            attack['timestamp'] = attack['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        # Get total count (with same filter)
        count_query = f"""
            SELECT COUNT(*) as total FROM attack_logs
            {where_clause}
        """

        count_params = (attack_type,) if where_clause else ()
        total = db.fetchone(count_query, count_params)['total']

        return jsonify({
            'attacks': attacks,
            'total': total,
            'pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-recent-events')
def get_recent_events():
    try:
        # Get last 10 attacks
        attacks_query = """
            SELECT 'attack' as type, attack_type as action, target_element as element, 
                   timestamp, blocked, risk_level
            FROM attack_logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        attacks = db.fetchall(attacks_query)
        
        # Get last 10 legitimate clicks
        clicks_query = """
            SELECT 'click' as type, 'legitimate_click' as action, element_clicked as element,
                   timestamp, NULL as blocked, 'safe' as risk_level
            FROM legitimate_clicks 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        clicks = db.fetchall(clicks_query)
        
        # Combine and sort
        events = attacks + clicks
        events = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:20]
        
        # Format timestamps
        for event in events:
            event['timestamp'] = event['timestamp'].strftime('%H:%M:%S')
        
        return jsonify({'events': events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create default admin user if not exists
    try:
        hashed = generate_password_hash('admin123')
        query = "UPDATE admin_users SET password_hash = %s WHERE username = 'admin'"
        db.execute(query, (hashed,))
    except:
        pass


@app.route('/test-console')
def test_console():
    return render_template('test_console.html')

app.run(debug=True, port=5000)
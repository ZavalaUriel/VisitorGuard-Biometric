from flask_socketio import emit, join_room, leave_room
from datetime import datetime

def register_socket_events(socketio):

    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {datetime.utcnow()}')
        emit('connection_response', {
            'status': 'connected',
            'message': 'Successfully connected to VisitorGuard',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {datetime.utcnow()}')
    
    @socketio.on('join')
    def handle_join(data):
     
        room = data.get('room', 'general')
        join_room(room)
        emit('joined_room', {
            'room': room,
            'message': f'Successfully joined room: {room}'
        })
        print(f'Client joined room: {room}')
    
    @socketio.on('leave')
    def handle_leave(data):
       
        room = data.get('room', 'general')
        leave_room(room)
        emit('left_room', {
            'room': room,
            'message': f'Successfully left room: {room}'
        })
        print(f'Client left room: {room}')
    
    @socketio.on('face_verification_request')
    def handle_face_verification(data):
        
        user_id = data.get('user_id')
        print(f'Face verification requested for user: {user_id}')
        
        emit('verification_in_progress', {
            'user_id': user_id,
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat()
        }, room='security')
    
    @socketio.on('verification_result')
    def handle_verification_result(data):
       
        emit('verification_completed', data, broadcast=True)
        print(f"Verification result: User {data.get('user_id')}, Verified: {data.get('verified')}")
    
    @socketio.on('visitor_check_in')
    def handle_check_in(data):
      
        emit('new_check_in', data, broadcast=True)
        print(f"Check-in: {data.get('name')} - Visit ID: {data.get('visit_id')}")
    
    @socketio.on('visitor_check_out')
    def handle_check_out(data):
        
        emit('check_out_completed', data, broadcast=True)
        print(f"Check-out: {data.get('name')} - Visit ID: {data.get('visit_id')}")
    
    @socketio.on('alert')
    def handle_alert(data):
       
        emit('security_alert', {
            **data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='security')
        print(f"Security Alert: {data.get('type')} - {data.get('message')}")
    
    @socketio.on('request_active_visits')
    def handle_request_active_visits():
       
        emit('active_visits_response', {
            'visits': [],
            'count': 0,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    print('✅ SocketIO events registered successfully')
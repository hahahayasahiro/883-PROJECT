"""Read-only verification of the browser demo state after restarting the server."""
import httpx

with httpx.Client(base_url='http://127.0.0.1:8000') as client:
    assert client.get('/api/health').json()['status']=='ok'
    assert client.post('/api/auth/login',json={'username':'student','password':'Campus2026!'}).status_code==200
    applications=client.get('/api/applications').json()['applications']
    assert any(a['status']=='approved' and a['decision_note']=='Verified synthetic student details. Ready to issue.' for a in applications)
    assert any(b['status']=='active' for b in client.get('/api/facilities').json()['bookings'])
    assert any(t['status']=='completed' and t['cost']==35 for t in client.get('/api/maintenance').json()['tickets'])
    client.post('/api/auth/logout')
print('PASS: approved application, active booking and completed repair survived a real server process restart.')

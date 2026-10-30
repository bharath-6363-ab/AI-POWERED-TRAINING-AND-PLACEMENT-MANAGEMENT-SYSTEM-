import uvicorn

if __name__ == '__main__':
    print('Starting AI-Powered Training & Placement Management System...')
    print('Web Portal: http://127.0.0.1:8080/static/index.html')
    print('API Docs:   http://127.0.0.1:8080/docs')
    uvicorn.run('backend.app.main:app', host='127.0.0.1', port=8080, reload=True)

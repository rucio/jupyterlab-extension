class MockHandler:
    def finish(*args, **kwargs):
        pass
    
    def current_user(*args, **kwargs):
        return None
    
    def get_json_body(*args, **kwargs):
        pass

    def get_query_argument(*args, **kwargs):
        pass

    def set_status(*args, **kwargs):
        pass
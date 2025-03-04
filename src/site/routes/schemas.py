from pydantic import BaseModel


from typing import Literal


class PageVariable(BaseModel):
    active_nav: Literal[
        'DASHBOARD', 
        'RECOMMENDATION',
        'ADMIN_USERS',
        'MATERIAL', 
        'PROFILE',
    ]
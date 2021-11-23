import os
from .models import ThingDescription, DirectoryNameToURL, TargetToChildName, TypeToChildrenNames, DynamicAttributes
from flask_pymongo import PyMongo

mongo = PyMongo()

def clear_database() -> None:
    """Drop collections in the mongodb database in order to initialize it.
    
    """
    ThingDescription.drop_collection()
    DirectoryNameToURL.drop_collection()
    TypeToChildrenNames.drop_collection()
    TargetToChildName.drop_collection()
    DynamicAttributes.drop_collection()


def init_dir_to_url(level: str) -> None:
    """Initialize name-to-URL mappings for the current directory using contents specified by 'level'
    
    Args:
        level(str): it specifies the level of current directory
    """
    level1_host = f'http://localhost:5001'
    level2a_host = f'http://localhost:5002'
    level2b_host = f'http://localhost:5003'
    level3aa_host = f'http://localhost:5004'
    level3ab_host = f'http://localhost:5005'
    level4aba_host = f'http://localhost:5006'
    level4abb_host = f'http://localhost:5007'
    level5abba_host = f'http://localhost:5008'
    level5abbb_host = f'http://localhost:5009'

    if os.getenv('CDN_DOMAIN'):
        level1_host = f'/level1'
        level2a_host = f'/level2a'
        level2b_host = f'/level2b'
        level3aa_host = f'/level3aa'
        level3ab_host = f'/level3ab'
        level4aba_host = f'/level4aba'
        level4abb_host = f'/level4abb'
        level5abba_host = f'/level5abba'
        level5abbb_host = f'/level5abbb'

    DirectoryNameToURL.drop_collection()
    if level == "level1":
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level1',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url=level2a_host, relationship='child').save()
        DirectoryNameToURL(directory_name='level2b',
                           url=level2b_host, relationship='child').save()
    elif level == 'level2a':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level1',
                           url=level1_host, relationship='parent').save()
        DirectoryNameToURL(directory_name='level3aa',
                           url=level3aa_host, relationship='child').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=level3ab_host, relationship='child').save()
    elif level == 'level2b':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level1',
                           url=level1_host, relationship='parent').save()
    elif level == 'level3aa':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url=level2a_host, relationship='parent').save()
    elif level == 'level3ab':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url=level2a_host, relationship='parent').save()
        DirectoryNameToURL(directory_name='level4aba',
                           url=level4aba_host, relationship='child').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=level4abb_host, relationship='child').save()
    elif level == 'level4aba':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=level3ab_host, relationship='parent').save()
    elif level == 'level4abb':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=level3ab_host, relationship='parent').save()
        DirectoryNameToURL(directory_name='level5abba',
                           url=level5abba_host, relationship='child').save()
        DirectoryNameToURL(directory_name='level5abbb',
                           url=level5abbb_host, relationship='child').save()
    elif level == 'level5abba':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=level4abb_host, relationship='parent').save()
    elif level == 'level5abbb':
        DirectoryNameToURL(directory_name='master',
                           url=level1_host, relationship='master').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=level4abb_host, relationship='parent').save()


def init_target_to_child_name(level: str) -> None:
    """Initialize the target-to-child mappings for the current directory

    Args:
        level(str): it specifies the level of current directory
    """
    if level == 'level1':
        TargetToChildName(target_name='level3aa', child_name='level2a').save()
        TargetToChildName(target_name='level3ab', child_name='level2a').save()
        TargetToChildName(target_name='level4aba', child_name='level2a').save()
        TargetToChildName(target_name='level4abb', child_name='level2a').save()
        TargetToChildName(target_name='level5abba', child_name='level2a').save()
        TargetToChildName(target_name='level5abbb', child_name='level2a').save()
    elif level == 'level2a':
        TargetToChildName(target_name='level4aba', child_name='level3ab').save()
        TargetToChildName(target_name='level4abb', child_name='level3ab').save()
        TargetToChildName(target_name='level5abba', child_name='level3ab').save()
        TargetToChildName(target_name='level5abbb', child_name='level3ab').save()
    elif level == 'level3ab':
        TargetToChildName(target_name='level5abba', child_name='level4abb').save()
        TargetToChildName(target_name='level5abbb', child_name='level4abb').save()
    else:
        pass

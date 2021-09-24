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

    DirectoryNameToURL.drop_collection()
    if level == "level1":
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url='http://localhost:5002', relationship='child').save()
        DirectoryNameToURL(directory_name='level2b',
                           url='http://localhost:5003', relationship='child').save()
    elif level == 'level2a':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level1',
                           url=f'http://localhost:5001', relationship='parent').save()
        DirectoryNameToURL(directory_name='level3aa',
                           url=f'http://localhost:5004', relationship='child').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=f'http://localhost:5005', relationship='child').save()
    elif level == 'level2b':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level1',
                           url=f'http://localhost:5001', relationship='parent').save()
    elif level == 'level3aa':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url=f'http://localhost:5002', relationship='parent').save()
    elif level == 'level3ab':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level2a',
                           url=f'http://localhost:5002', relationship='parent').save()
        DirectoryNameToURL(directory_name='level4aba',
                           url=f'http://localhost:5006', relationship='child').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=f'http://localhost:5007', relationship='child').save()
    elif level == 'level4aba':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=f'http://localhost:5005', relationship='parent').save()
    elif level == 'level4abb':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level3ab',
                           url=f'http://localhost:5005', relationship='parent').save()
        DirectoryNameToURL(directory_name='level5abba',
                           url=f'http://localhost:5008', relationship='child').save()
        DirectoryNameToURL(directory_name='level5abbb',
                           url=f'http://localhost:5009', relationship='child').save()
    elif level == 'level5abba':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=f'http://localhost:5007', relationship='parent').save()
    elif level == 'level5abbb':
        DirectoryNameToURL(directory_name='master',
                           url=f'http://localhost:5001', relationship='master').save()
        DirectoryNameToURL(directory_name='level4abb',
                           url=f'http://localhost:5007', relationship='parent').save()


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

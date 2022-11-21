from annotation_tool.backend.models import delete_tables

if __name__ == '__main__':
    if input('This will delete all tables! Do you want to proceed? y/n: ').lower() == 'y':
        delete_tables()

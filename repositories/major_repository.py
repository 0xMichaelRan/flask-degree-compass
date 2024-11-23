from services.db_service import DatabaseService

class MajorRepository:
    @staticmethod
    def get_categories():
        return DatabaseService.execute_query(
            'SELECT * FROM categories ORDER BY category_id'
        )

    @staticmethod
    def get_subjects(category_id, page_size, offset):
        count_query = 'SELECT COUNT(*) FROM subjects'
        count_params = None
        
        if category_id:
            count_query += ' WHERE category_id = %s'
            count_params = (category_id,)
        
        count = DatabaseService.execute_single_query(count_query, count_params)['count']
        
        query = '''
            SELECT s.*, c.category_name 
            FROM subjects s 
            JOIN categories c ON s.category_id = c.category_id 
        '''
        
        params = []
        if category_id:
            query += ' WHERE s.category_id = %s'
            params.append(category_id)
        
        query += ' ORDER BY s.subject_id LIMIT %s OFFSET %s'
        params.extend([page_size, offset])
        
        subjects = DatabaseService.execute_query(query, tuple(params))
        return subjects, count

    @staticmethod
    def get_majors(category_id, subject_id, page_size, offset):
        # Build count query based on filters
        count_query = 'SELECT COUNT(*) FROM majors m'
        count_params = []
        
        if subject_id:
            count_query += ' WHERE subject_id = %s'
            count_params.append(subject_id)
        elif category_id:
            count_query += ' JOIN subjects s ON m.subject_id = s.subject_id WHERE s.category_id = %s'
            count_params.append(category_id)
            
        count = DatabaseService.execute_single_query(count_query, tuple(count_params))['count']
        
        # Build data query
        query = '''
            SELECT m.*, s.subject_name, c.category_name 
            FROM majors m
            JOIN subjects s ON m.subject_id = s.subject_id
            JOIN categories c ON s.category_id = c.category_id
        '''
        
        params = []
        if subject_id:
            query += ' WHERE m.subject_id = %s'
            params.append(subject_id)
        elif category_id:
            query += ' WHERE c.category_id = %s'
            params.append(category_id)
            
        query += ' ORDER BY m.major_id LIMIT %s OFFSET %s'
        params.extend([page_size, offset])
        
        majors = DatabaseService.execute_query(query, tuple(params))
        return majors, count

    @staticmethod
    def get_major_by_id(major_id):
        return DatabaseService.execute_single_query(
            '''
            SELECT m.*, s.subject_name, c.category_name 
            FROM majors m
            JOIN subjects s ON m.subject_id = s.subject_id
            JOIN categories c ON s.category_id = c.category_id
            WHERE m.major_id = %s
            ''',
            (major_id,)
        )

    @staticmethod
    def save_major_qa(major_id, qa_sql_statements):
        try:
            # First delete existing QA
            DatabaseService.execute_query(
                'DELETE FROM major_qa WHERE major_id = %s',
                (major_id,)
            )
            
            # Execute each INSERT statement
            executed_count = 0
            for sql_statement in qa_sql_statements.strip().split('\n'):
                if sql_statement.strip():
                    DatabaseService.execute_query(sql_statement)
                    executed_count += 1
            
            print(f"Executed {executed_count} INSERT statements for major {major_id}")
            
            # Return all QA for this major
            result = DatabaseService.execute_query(
                'SELECT * FROM major_qa WHERE major_id = %s ORDER BY id',
                (major_id,)
            )
            print(f"Retrieved {len(result)} QA pairs for major {major_id}")
            return result
            
        except Exception as e:
            print(f"Error in save_major_qa for major {major_id}: {str(e)}")
            raise

    @staticmethod
    def get_major_qa(major_id):
        return DatabaseService.execute_single_query(
            'SELECT * FROM major_qa WHERE major_id = %s',
            (major_id,)
        )

    @staticmethod
    def save_major_intro(major_id, intro_content):
        result = DatabaseService.execute_single_query(
            '''
            INSERT INTO major_intro (major_id, intro_content)
            VALUES (%s, %s)
            ON CONFLICT (major_id) 
            DO UPDATE SET intro_content = EXCLUDED.intro_content, updated_at = CURRENT_TIMESTAMP
            RETURNING *
            ''',
            (major_id, intro_content)
        )
        return result

    @staticmethod
    def get_major_intro(major_id):
        return DatabaseService.execute_single_query(
            'SELECT * FROM major_intro WHERE major_id = %s',
            (major_id,)
        )
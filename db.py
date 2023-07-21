import sqlite3 as sq

db = sq.connect('tasks.db')
cursor = db.cursor()
async def db_start():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_text TEXT NOT NULL,
        done BOOLEAN DEFAULT 0)''')
    db.commit()


async def add_task_to_db(state):
    # Make sure 'user_id' and 'task_text' are set before accessing them
    async with state.proxy() as data:
        if 'user_id' in data and 'task_text' in data:
            cursor.execute("INSERT INTO tasks (user_id, task_text) VALUES (?, ?)", (data['user_id'], data['task_text']))
            db.commit()


async def get_users_task_from_db(id):
    cursor.execute("SELECT * FROM tasks WHERE user_id=?", (id,))
    result = cursor.fetchall()
    return result

async def get_undone_users_task_from_db(id):
    cursor.execute("SELECT * FROM tasks WHERE user_id=? and done=0", (id,))
    result = cursor.fetchall()
    return result

async def update_users_task_in_db(user_id, task_id):
    # Use a parameterized query to avoid SQL injection
    cursor.execute("UPDATE tasks SET done=1 WHERE user_id=? AND id=?", (user_id, task_id))
    
    # Commit the changes to the database
    db.commit()


async def delete_users_task_from_db(userid,taskid):
    cursor.execute("DELETE FROM tasks WHERE user_id=? AND ID=?", (userid,taskid))
    db.commit()


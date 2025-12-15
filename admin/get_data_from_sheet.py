from flask import render_template, session, redirect, url_for
import requests
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import csv, io, json

# other python files
import x

from app import app

@app.get("/get-data-from-sheet")
def get_data_from_sheet():
    try:

        # Validate user is admin
        ################
        user = session.get("user")
        if not user: return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################
 
        # key: 1UYgE2jJ__HYl0N7lA5JR3sMH75hwhzhPPsSRRA-WNdg
        url= f"https://docs.google.com/spreadsheets/d/{x.google_spread_sheet_key}/export?format=csv&id={x.google_spread_sheet_key}"
        res=requests.get(url=url)
        # return(res.text) # retuns a page if there is an error
        csv_text = res.content.decode('utf-8')
        csv_file = io.StringIO(csv_text) # Use StringIO to treat the string as a file
       
        data = {}
        reader = csv.DictReader(csv_file)
        #ic(reader)
        # Convert each row into the desired structure
        for row in reader:
            item = {
                    'english': row['english'],
                    'danish': row['danish'],
                    'spanish': row['spanish']
               
            }
            data[row['key']] = (item)
 
        # Convert the data to JSON
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        # ic(data)
 
        # Save data to the file
        with open("dictionary.json", 'w', encoding='utf-8') as f:
            f.write(json_data)

        header = render_template("global/header.html")
 
        return f""" 
            {header}
            <main class="dictionary"> 
                <h1>Hi admin user</h1>
                <h2> Data has been saved! </h2>
                <br>
                {json_data}
            </main>
            </body></html>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
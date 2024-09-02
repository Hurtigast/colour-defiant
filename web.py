from flask import Flask, render_template, request
import api
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        #Get form data
        name_tag = request.form['name']
        name_tag_split = name_tag.split("#")
        name = name_tag_split[0]
        tag = name_tag_split[1]

        user = api.get_puiid(name,tag)
        test = api.get_match(user)
        #Return answer
        return render_template('user.html', message=test)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
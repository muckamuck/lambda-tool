from utility import FlaskLambda

app = FlaskLambda(__name__)


@app.route('/foo', methods=['GET', 'POST'])
def foo():
    data = {
        'form': request.form.copy(),
        'args': request.args.copy(),
        'json': request.json
    }
    return (
        json.dumps(data, indent=4, sort_keys=True),
        200,
        {'Content-Type': 'application/json'}
    )


if __name__ == '__main__':
    app.run(debug=True)


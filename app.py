from flask import Flask, render_template, request, jsonify
from astro_engine import calculate_chart, search_places


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search_place")
def search_place():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "success": True,
            "places": []
        })

    try:
        places = search_places(query)

        return jsonify({
            "success": True,
            "places": places
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "places": [],
            "error": str(e)
        })


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json(force=True)

        date = data.get("date", "").strip()
        time = data.get("time", "").strip()
        city = data.get("city", "").strip()
        mode = data.get("mode", "client")

        lat = data.get("lat")
        lon = data.get("lon")
        display_name = data.get("display_name")

        chart = calculate_chart(
            date_str=date,
            time_str=time,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        chart["mode"] = mode

        return jsonify({
            "success": True,
            "chart": chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/calculate_transit", methods=["POST"])
def calculate_transit():
    try:
        data = request.get_json(force=True)

        date = data.get("date", "").strip()
        time = data.get("time", "").strip()
        city = data.get("city", "").strip()

        lat = data.get("lat")
        lon = data.get("lon")
        display_name = data.get("display_name")

        transit_chart = calculate_chart(
            date_str=date,
            time_str=time,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        return jsonify({
            "success": True,
            "transit": transit_chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/rectification", methods=["POST"])
def rectification():
    try:
        data = request.get_json(force=True)

        date = data.get("date", "").strip()
        time = data.get("time", "").strip()
        city = data.get("city", "").strip()

        lat = data.get("lat")
        lon = data.get("lon")
        display_name = data.get("display_name")

        rectified_chart = calculate_chart(
            date_str=date,
            time_str=time,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        return jsonify({
            "success": True,
            "chart": rectified_chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
)

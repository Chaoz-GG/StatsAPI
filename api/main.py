from flask import Flask, jsonify
from utils.main import mm_stats_exist, faceit_stats_exist, get_mm_stats, get_faceit_stats, collect_mm_stats, \
    collect_faceit_stats, insert_mm_stats, insert_faceit_stats, update_mm_stats, update_faceit_stats

app = Flask(__name__)


@app.route('/stats/view/mm/<int:steam_id>', methods=['GET', 'POST'])
def mm_stats_view(steam_id):
    if mm_stats_exist(steam_id):
        _stats = get_mm_stats(steam_id)

        _stats = {
            "rank": _stats[1],
            "kpd": _stats[2],
            "rating": _stats[3],
            "clutch": _stats[4],
            "best_weapon": _stats[5],
            "win_rate": _stats[6],
            "hs": _stats[7],
            "adr": _stats[8],
            "entry_success": _stats[9],
            "most_played_map": _stats[10],
            "most_successful_map": _stats[11]
        }

        return jsonify(_stats)

    else:
        _stats = collect_mm_stats(steam_id)

        if not _stats:
            return jsonify({
                "error": "The Steam ID provided is invalid."
            })

        insert_mm_stats(steam_id, _stats)

        return jsonify(_stats)


@app.route('/stats/view/faceit/<int:steam_id>', methods=['GET', 'POST'])
def faceit_stats_view(steam_id):
    if faceit_stats_exist(steam_id):
        _stats = get_faceit_stats(steam_id)

        _stats = {
            "rank": _stats[1],
            "elo": _stats[2],
            "kpd": _stats[3],
            "rating": _stats[4],
            "win_rate": _stats[5],
            "hs": _stats[6],
            "matches": _stats[7],
            "most_played_map": _stats[8],
            "most_successful_map": _stats[9]
        }

        return jsonify(_stats)

    else:
        _stats = collect_faceit_stats(steam_id)

        if not _stats:
            return jsonify({
                "error": "No FaceIT stats found for the given Steam ID."
            })

        insert_faceit_stats(steam_id, _stats)

        return jsonify(_stats)


@app.route('/stats/update/mm/<int:steam_id>', methods=['GET', 'POST'])
def mm_stats_update(steam_id):
    if mm_stats_exist(steam_id):
        _stats = collect_mm_stats(steam_id)

        update_mm_stats(steam_id, _stats)

        return jsonify({
            "message": "The stats have been updated."
        })

    else:
        return jsonify({
            "error": "No stats currently exist for this Steam ID."
        })


@app.route('/stats/update/faceit/<int:steam_id>', methods=['GET', 'POST'])
def faceit_stats_update(steam_id):
    if faceit_stats_exist(steam_id):
        _stats = collect_faceit_stats(steam_id)

        update_faceit_stats(steam_id, _stats)

        return jsonify({
            "message": "The stats have been updated."
        })

    else:
        return jsonify({
            "error": "No stats currently exist for this Steam ID."
        })


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

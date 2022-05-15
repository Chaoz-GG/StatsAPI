from flask_selfdoc import Autodoc
from flask import Flask, jsonify
from utils.main import non_empty_mm_stats_exist, non_empty_faceit_stats_exist, get_mm_stats, get_faceit_stats, \
    collect_mm_stats, collect_faceit_stats, insert_mm_stats, insert_faceit_stats, \
    update_mm_stats, update_faceit_stats, get_inventory

app = Flask(__name__)

auto = Autodoc(app)


@auto.doc()
@app.route('/stats/view/mm/<int:steam_id>', methods=['GET'])
def mm_stats_view(steam_id):
    """
    Return matchmaking stats for the given Steam ID.

    responses:
        200:
            description: Stats generated / found for the given Steam ID
        404:
            description: No stats found for the given Steam ID
    """

    if non_empty_mm_stats_exist(steam_id):
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
            insert_mm_stats(steam_id)

            return jsonify({
                "error": "No stats found for the given Steam ID."
            }), 404

        if non_empty_mm_stats_exist(steam_id):
            update_mm_stats(steam_id, _stats)

        else:
            insert_mm_stats(steam_id, _stats)

        return jsonify(_stats)


@auto.doc()
@app.route('/stats/view/faceit/<int:steam_id>', methods=['GET'])
def faceit_stats_view(steam_id):
    """
    Return FaceIT stats for the given Steam ID.

    responses:
        200:
            description: Stats generated / found for the given Steam ID
        404:
            description: No stats found for the given Steam ID
    """

    if non_empty_faceit_stats_exist(steam_id):
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
            insert_faceit_stats(steam_id)

            return jsonify({
                "error": "No stats found for the given Steam ID."
            }), 404

        if non_empty_faceit_stats_exist(steam_id):
            update_faceit_stats(steam_id, _stats)

        else:
            insert_faceit_stats(steam_id, _stats)

        return jsonify(_stats)


@auto.doc()
@app.route('/stats/update/mm/<int:steam_id>', methods=['GET'])
def mm_stats_update(steam_id):
    """
    Update matchmaking stats for the given Steam ID.

    responses:
        200:
            description: Stats generated / found for the given Steam ID
        404:
            description: No stats found for the given Steam ID
    """

    if non_empty_mm_stats_exist(steam_id):
        _stats = collect_mm_stats(steam_id)

        if not _stats:
            insert_mm_stats(steam_id)

            return jsonify({
                "error": "No stats found for the given Steam ID."
            }), 404

        update_mm_stats(steam_id, _stats)

        return jsonify({
            "message": "The stats have been updated."
        })

    else:
        return jsonify({
            "error": "No stats currently exist for the given Steam ID."
        }), 404


@auto.doc()
@app.route('/stats/update/faceit/<int:steam_id>', methods=['GET'])
def faceit_stats_update(steam_id):
    """
    Update FaceIT stats for the given Steam ID.

    responses:
        200:
            description: Stats generated / found for the given Steam ID
        404:
            description: No stats found for the given Steam ID
    """

    if non_empty_faceit_stats_exist(steam_id):
        _stats = collect_faceit_stats(steam_id)

        if not _stats:
            insert_faceit_stats(steam_id)

            return jsonify({
                "error": "No stats found for the given Steam ID."
            }), 404

        update_faceit_stats(steam_id, _stats)

        return jsonify({
            "message": "The stats have been updated."
        })

    else:
        return jsonify({
            "error": "No stats currently exist for the given Steam ID."
        }), 404


@auto.doc()
@app.route('/inventory/<int:steam_id>', methods=['GET'])
def inventory(steam_id):
    """
    Update FaceIT stats for the given Steam ID.

    responses:
        200:
            description: Inventory details found for the given Steam ID
        404:
            description: No inventory details found for the given Steam ID
    """

    _inv = get_inventory(steam_id)

    if _inv:
        return jsonify(_inv)

    else:
        return jsonify({
            "error": "No inventory details found for the given steam ID."
        }), 404


@app.route('/docs')
def docs():
    return auto.html()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

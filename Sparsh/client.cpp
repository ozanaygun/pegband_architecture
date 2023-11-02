#include <bits/stdc++.h>
using namespace std;

// these includes may need to be modified depending on your system
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#ifdef LOCAL
    #include "./debug.h"
#else
    #define debug(x...) 42
#endif

#define rep(i, a, b) for(int i = a; i < (b); ++i) 
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()
typedef long long ll;
typedef pair<int, int> pii; 
typedef vector<int> vi;
#define nl '\n'

/* ------ GLOBALS ------ */
string BOT_NAME = "Sparsh C++";
const int SEED = 87;
const int TOTAL_TIME_MS = 100 * 1000;
const int THREAD_COUNT = 16;
mt19937 RNG(SEED); // (chrono::steady_clock::now().time_since_epoch().count());
/* -------------------------- */


/* ------ KACTL GEOMETRY TEMPLATE ---- */
template <class T> int sgn(T x) { return (x > 0) - (x < 0); }

template<class T>
struct Point {
	typedef Point P;
	T x, y;
	explicit Point(T x=0, T y=0) : x(x), y(y) {}
	bool operator<(P p) const { return tie(x,y) < tie(p.x,p.y); }
	bool operator==(P p) const { return tie(x,y)==tie(p.x,p.y); }
	P operator+(P p) const { return P(x+p.x, y+p.y); }
	P operator-(P p) const { return P(x-p.x, y-p.y); }
	P operator*(T d) const { return P(x*d, y*d); }
	P operator/(T d) const { return P(x/d, y/d); }
	T dot(P p) const { return x*p.x + y*p.y; }
	T cross(P p) const { return x*p.y - y*p.x; }
	T cross(P a, P b) const { return (a-*this).cross(b-*this); }
	T dist2() const { return x*x + y*y; }
	double dist() const { return sqrt((double)dist2()); }
	// angle to x-axis in interval [-pi, pi]
	double angle() const { return atan2(y, x); }
	P unit() const { return *this/dist(); } // makes dist()=1
	P perp() const { return P(-y, x); } // rotates +90 degrees
	P normal() const { return perp().unit(); }
	// returns point rotated 'a' radians ccw around the origin
	P rotate(double a) const {
		return P(x*cos(a)-y*sin(a),x*sin(a)+y*cos(a)); }
	friend ostream& operator<<(ostream& os, P p) {
		return os << "(" << p.x << "," << p.y << ")"; }
};

template<class P> bool onSegment(P s, P e, P p) {
    return p.cross(s, e) == 0 && (s - p).dot(e - p) <= 0;
}

template<class P> vector<P> segInter(P a, P b, P c, P d) {
	auto oa = c.cross(d, a), ob = c.cross(d, b),
	     oc = a.cross(b, c), od = a.cross(b, d);
	// Checks if intersection is single non-endpoint point.
	if (sgn(oa) * sgn(ob) < 0 && sgn(oc) * sgn(od) < 0)
		return {(a * ob - b * oa) / (ob - oa)};
	set<P> s;
	if (onSegment(c, d, a)) s.insert(a);
	if (onSegment(c, d, b)) s.insert(b);
	if (onSegment(a, b, c)) s.insert(c);
	if (onSegment(a, b, d)) s.insert(d);
	return {all(s)};
}

using pt = Point<double>;
int orientation(pt a, pt b, pt c) {
    double v = a.x*(b.y-c.y)+b.x*(c.y-a.y)+c.x*(a.y-b.y);
    if (v < 0) return -1; // clockwise
    if (v > 0) return +1; // counter-clockwise
    return 0;
}

bool cw(pt a, pt b, pt c, bool include_collinear) {
    int o = orientation(a, b, c);
    return o < 0 || (include_collinear && o == 0);
}
bool ccw(pt a, pt b, pt c, bool include_collinear) {
    int o = orientation(a, b, c);
    return o > 0 || (include_collinear && o == 0);
}

void convex_hull(vector<pt>& a, bool include_collinear = false) {
    if (a.size() == 1)
        return;

    sort(a.begin(), a.end(), [](pt a, pt b) {
        return make_pair(a.x, a.y) < make_pair(b.x, b.y);
    });
    pt p1 = a[0], p2 = a.back();
    vector<pt> up, down;
    up.push_back(p1);
    down.push_back(p1);
    for (int i = 1; i < static_cast<int>(a.size()); i++) {
        if (i == static_cast<int>(a.size()) - 1 || cw(p1, a[i], p2, include_collinear)) {
            while (up.size() >= 2 && !cw(up[up.size()-2], up[up.size()-1], a[i], include_collinear))
                up.pop_back();
            up.push_back(a[i]);
        }
        if (i == static_cast<int>(a.size()) - 1 || ccw(p1, a[i], p2, include_collinear)) {
            while (down.size() >= 2 && !ccw(down[down.size()-2], down[down.size()-1], a[i], include_collinear))
                down.pop_back();
            down.push_back(a[i]);
        }
    }

    if (include_collinear && up.size() == a.size()) {
        reverse(a.begin(), a.end());
        return;
    }
    a.clear();
    for (int i = 0; i < (int)up.size(); i++)
        a.push_back(up[i]);
    for (int i = down.size() - 2; i > 0; i--)
        a.push_back(down[i]);
}

template<class P>
int sideOf(P s, P e, P p) { return sgn(s.cross(e, p)); }

template<class P>
int sideOf(const P& s, const P& e, const P& p, double eps) {
	auto a = (e-s).cross(p-s);
	double l = (e-s).dist()*eps;
	return (a > l) - (a < -l);
}

// TODO: check if having collinear points in polygon causes problems
// TODO: try collinear line case for size = 2
// TODO: test thoroughly and cleanup
bool inHull(const vector<Point<double>>& l, Point<double> p, bool strict = true) {
	int a = 1, b = sz(l) - 1, r = !strict;
	if (sz(l) < 3) return r && onSegment(l[0], l.back(), p);
	if (sideOf(l[0], l[a], l[b]) > 0) swap(a, b);
	if (sideOf(l[0], l[a], p) >= r || sideOf(l[0], l[b], p)<= -r)
		return false;
	while (abs(a - b) > 1) {
		int c = (a + b) / 2;
		(sideOf(l[0], l[c], p) > 0 ? b : a) = c;
	}
	return sgn(l[a].cross(l[b], p)) < r;
}
/* -------------------------- */

mutex m;
int shared_best_peg, shared_best_score, shared_best_my, shared_best_opp;
int shared_best_tiebreaker, shared_trials;
vector<int> shared_idxs;

struct Bot {
    const int BOARD_HEIGHT;
    const int BOARD_WIDTH;
    const int BOARD_CELLS;
    const int PEG_COUNT;
    const int RUBBERBAND_COUNT;
    const int MY_COLOR;
    const int OPP_COLOR;
    const int PEG_PLACEMENT_TIME;
    vector<int> board;
    vector<vector<int>> pegs;
    vector<vector<int>> rubber_bands;

    Bot(int board_height, int board_width, int peg_count, int rubberband_count, int color) :
        BOARD_HEIGHT(board_height), BOARD_WIDTH(board_width), BOARD_CELLS(board_height * board_width), 
        PEG_COUNT(peg_count), RUBBERBAND_COUNT(rubberband_count), MY_COLOR(color), OPP_COLOR(3 - color),
        PEG_PLACEMENT_TIME(TOTAL_TIME_MS / peg_count) {
            debug(PEG_PLACEMENT_TIME);
            board.resize(BOARD_CELLS, 0);
            pegs.resize(3, vector<int>());
    }

    void update(vector<int>& board) {
        this->board = board;
        vector<int>& opp_pegs = pegs[OPP_COLOR];
        for (int i = 0; i < BOARD_CELLS; ++i) {
            if (board[i] == OPP_COLOR
                && find(opp_pegs.begin(), opp_pegs.end(), i) == opp_pegs.end())
                opp_pegs.push_back(i);
        }
    }

    template<class T>
    Point<T> pegToPoint(int peg) {
        return Point<T>((peg / BOARD_WIDTH) + 0.5, (peg % BOARD_WIDTH) + 0.5);
    }

    template<class T>
    vector<Point<T>> getSquare(int peg) {
        Point<T> p = pegToPoint<T>(peg);
        return {p + Point<T>(-0.5, -0.5), p + Point<T>(-0.5, 0.5),
                p + Point<T>(0.5, 0.5), p + Point<T>(0.5, -0.5)};
    }

    bool onSegmentPeg(int peg_p1, int peg_p2, int peg_q) {
        Point<double> p1 = pegToPoint<double>(peg_p1);
        Point<double> p2 = pegToPoint<double>(peg_p2);
        Point<double> q = pegToPoint<double>(peg_q);
        return onSegment(p1, p2, q);
    }

    bool crossesSquare(int peg_p1, int peg_p2, int peg_q, bool debug_flag = false) {
        Point<double> p1 = pegToPoint<double>(peg_p1);
        Point<double> p2 = pegToPoint<double>(peg_p2);
        vector<Point<double>> square = getSquare<double>(peg_q);
        vector<Point<double>> squareInter;
        for (int i = 0; i < 4; ++i) {
            auto inter = segInter(p1, p2, square[i], square[(i + 1) % 4]);
            assert(inter.size() <= 1);
            if (inter.size() == 1 && 
                find(squareInter.begin(), squareInter.end(), inter[0]) == squareInter.end()) {
                squareInter.push_back(inter[0]);
            }
        }
        if (debug_flag) {
            for (auto x : squareInter) {
                cout << x << ", ";
            }
            cout << nl;
        }
        assert(squareInter.size() <= 2);
        return squareInter.size() == 2;
    }

    bool orderPolygon(vector<int>& pegs, bool debug_flag = false) {
        vector<Point<double>> points;
        for (int i : pegs) {
            points.push_back(pegToPoint<double>(i));
        }
        vector<Point<double>> hull = points;
        if (debug_flag) {
            cout << "points: ";
            for (auto p : hull) {
                cout << p << ", ";
            }
            cout << nl;
        }
        convex_hull(hull, true);
        if (debug_flag) {
            cout << "hull: ";
            for (auto p : hull) {
                cout << p << ", ";
            }
            cout << nl;
        }
        if (hull.size() != points.size()) {
            return false;
        }
        vector<int> hull_pegs;
        for (auto p : hull) {
            int x = static_cast<int>(p.x - 0.5);
            int y = static_cast<int>(p.y - 0.5);
            hull_pegs.push_back(x * BOARD_WIDTH + y); // relies on proper int casting
        }
        pegs = hull_pegs;
        return true;
    }

    bool polygonContainsPeg(vector<int>& polygon, int peg) {
        vector<Point<double>> polyPoints;
        for (int i : polygon) {
            polyPoints.push_back(pegToPoint<double>(i));
        }
        return inHull(polyPoints, pegToPoint<double>(peg));
    }

    bool polygonCrossesSquare(vector<int>& polygon, int peg) {
        vector<Point<double>> polyPoints;
        for (int i : polygon) {
            polyPoints.push_back(pegToPoint<double>(i));
        }
        vector<Point<double>> square = getSquare<double>(peg);
        vector<Point<double>> squareInter;
        for (int i = 0; i < static_cast<int>(polygon.size()); ++i) {
            auto p1 = polyPoints[i];
            auto p2 = polyPoints[(i + 1) % polygon.size()];
            for (int j = 0; j < 4; ++j) {
                auto inter = segInter(p1, p2, square[j], square[(j + 1) % 4]);
                assert(inter.size() <= 1);
                if (inter.size() == 1 && 
                    find(squareInter.begin(), squareInter.end(), inter[0]) == squareInter.end()) {
                    squareInter.push_back(inter[0]);
                }
            }
        }
        return squareInter.size() >= 2;
    }

    int score(const vector<int>& pegs, const vector<int>& opp_pegs, bool store = false) {
        vector<int> board(BOARD_CELLS, 0);
        for (int i : pegs)
            board[i] = MY_COLOR;
        for (int i : opp_pegs)
            board[i] = OPP_COLOR;
        int peg_count = pegs.size();
        vector<bool> skip(1 << peg_count, false);
        vector<bool> valid(1 << peg_count, false);
        vector<vector<int>> convex_polygon(1 << peg_count);
        vector<vector<int>> contained(1 << peg_count);
        for (int mask = (1 << peg_count) - 1; mask >= 1; --mask) {
            if (skip[mask]) {
                for (int i = 0; i < peg_count; ++i) {
                    if ((mask >> i) & 1) {
                        skip[mask ^ (1 << i)] = true;
                    }
                }
                continue;
            }
            int polygon_size = __builtin_popcount(mask);
            if (polygon_size == 1) {
                int peg = pegs[__builtin_ctz(mask)];
                valid[mask] = true;
                skip[0] = true;
                convex_polygon[mask].push_back(peg);
                contained[mask].push_back(peg);
                continue;
            }
            if (polygon_size == 2) {
                bool rule_broken = false;
                int p1 = pegs[__builtin_ctz(mask)];
                int p2 = pegs[__builtin_ctz(mask ^ (mask & -mask))];

                // check if any opponent pegs in between
                for (int q : opp_pegs) {
                    // debug(p1, p2, q, onSegmentPeg(p1, p2, q));
                    if (onSegmentPeg(p1, p2, q)) {
                        rule_broken = true;
                        break;
                    }
                }

                // find intersecting squares
                vector<bool> inter(BOARD_CELLS, false);
                inter[p1] = true;
                inter[p2] = true;
                for (int i = 0; i < BOARD_CELLS; ++i) {
                    if (board[i] == OPP_COLOR) continue;
                    if (crossesSquare(p1, p2, i)) {
                        // debug("CROSS", q);
                        inter[i] = true;
                    }
                }
                
                if (rule_broken) continue;

                valid[mask] = true;
                convex_polygon[mask].push_back(pegs[__builtin_ctz(mask)]);
                convex_polygon[mask].push_back(pegs[__builtin_ctz(mask ^ (mask & -mask))]);
                // int count = 0;
                for (int i = 0; i < BOARD_CELLS; ++i) {
                    if (inter[i]) {
                        contained[mask].push_back(i);
                    }
                }
                // cout << setw(5) << bitset<4>(mask) << setw(5) << contained[mask].size() << endl;
                for (int i = 0; i < peg_count; ++i) {
                    if ((mask >> i) & 1) {
                        skip[mask ^ (1 << i)] = true;
                    }
                }
                
                continue;
            }

            // convex polygons with size >= 3
            vector<int> polygon;
            for (int i = 0; i < peg_count; ++i) {
                if ((mask >> i) & 1) {
                    polygon.push_back(pegs[i]);
                }
            }
            // if (store) {
            //     debug("poly", polygon);
            // }
            if (!orderPolygon(polygon)) {
                continue;
            }
            // if (store) {
            //     debug("hull", polygon);
            // }
            bool rule_broken = false;
            for (int i = 0; i < static_cast<int>(polygon.size()); ++i) {
                int p1 = polygon[i];
                int p2 = polygon[(i + 1) % polygon.size()];
                for (int q : opp_pegs) {
                    // debug(p1, p2, q, onSegmentPeg(p1, p2, q));
                    if (onSegmentPeg(p1, p2, q)) {
                        rule_broken = true;
                        break;
                    }
                }
                if (rule_broken) break;
            }

            for (int q : opp_pegs) {
                if (polygonContainsPeg(polygon, q)) {
                    rule_broken = true;
                    break;
                }
            }

            if (store) {
                // debug(rule_broken);
            }
            
            if (rule_broken) continue;

            // [DONE] TODO: assumption that one of the corners must be contained is wrong, need to use cross
            // a) peg check, not need of corners
            // b) check for more than 2 distinct intersecting points among all lines
            // find all intersecting points with the line
            // find intersecting squares
            vector<bool> inter(BOARD_CELLS, false);
            for (int i : polygon) {
                inter[i] = true;
            }
            for (int i = 0; i < BOARD_CELLS; ++i) {
                if (board[i] == OPP_COLOR) continue;
                if (polygonContainsPeg(polygon, i) || polygonCrossesSquare(polygon, i)) {
                    inter[i] = true;
                }
            }

            valid[mask] = true;
            convex_polygon[mask] = polygon;
            // int count = 0;
            for (int i = 0; i < BOARD_CELLS; ++i) {
                if (inter[i]) {
                    contained[mask].push_back(i);
                }
            }
            // if (store) {
            //     cout << setw(5) << bitset<20>(mask) << setw(5) << contained[mask].size() << endl;
            // }
            for (int i = 0; i < peg_count; ++i) {
                if ((mask >> i) & 1) {
                    skip[mask ^ (1 << i)] = true;
                }
            }
        } 
        
        vector<int> vis(BOARD_CELLS, 0);
        for (int iter = 0; iter < RUBBERBAND_COUNT; ++iter) {
            int best_mask = 0, best_count = 0;
            for (int mask = 1; mask < (1 << peg_count); ++mask) {
                if (!valid[mask]) continue;
                int count = 0;
                for (int i : contained[mask]) {
                    if (!vis[i]) {
                        ++count;
                    }
                }
                // cout << setw(5) << bitset<2>(mask) << setw(5) << count << endl;
                if (count > best_count) {
                    best_count = count;
                    best_mask = mask;
                }
            }
            // debug(best_count, best_mask, contained[best_mask]);
            for (int i : contained[best_mask]) {
                vis[i]++;
            }
            if (store) {
                rubber_bands.push_back(convex_polygon[best_mask]);
            }
        }
        // debug(vis);
        int count = 0;
        int total = 0;
        for (int i = 0; i < BOARD_CELLS; ++i) {
            if (vis[i]) {
                ++count;
                total += vis[i];
            }
        }
        if (store) {
            debug(count, total);
            // for (int i = 0; i < BOARD_HEIGHT; ++i) {
            //     for (int j = 0; j < BOARD_WIDTH; ++j) {
            //         const int v = i * BOARD_WIDTH + j;
            //         if (board[v] == 1) {
            //             cout << "G";
            //         }
            //         else if (board[v] == 2) {
            //             cout << "B";
            //         }
            //         else if (vis[v]) {
            //             cout << (MY_COLOR == 1 ? "g" : "b");
            //         }
            //         else
            //             cout << "*";
            //         cout << " ";
            //     }
            //     cout << nl;
            // }
        }
        
        return count;
    }

    
    void thread_fun(int thread_id, int left, int right) {
        vector<int> my_pegs = pegs[MY_COLOR];
        vector<int> opp_pegs = pegs[OPP_COLOR];
        int best_peg = -1;
        int best_score = numeric_limits<int>::min();
        int best_my = -1;
        int best_opp = -1;
        int best_tiebreaker = numeric_limits<int>::max();
        int trials = 0;
        const vector<int>& idxs = shared_idxs;
        auto start_time = chrono::steady_clock::now();

        for (int iter = left; iter < right; ++iter) {
            int i = idxs[iter];
            if (board[i] != 0) continue;
            auto end_time = chrono::steady_clock::now();
            auto diff = end_time - start_time;
            if (chrono::duration <double, milli> (diff).count() > PEG_PLACEMENT_TIME) {
                break;
            }
            ++trials;
            
            my_pegs.push_back(i);
            int my_score = this->score(my_pegs, opp_pegs);
            int opp_score = this->score(opp_pegs, my_pegs);
            int tiebreaker = min(i / BOARD_WIDTH, BOARD_HEIGHT - 1 - i / BOARD_WIDTH)
                            + min(i % BOARD_WIDTH, BOARD_WIDTH - 1 - i % BOARD_WIDTH);
            if (my_score - opp_score > best_score 
                || (my_score - opp_score == best_score && tiebreaker < best_tiebreaker)) {
                best_score = my_score - opp_score;
                best_peg = i;
                best_my = my_score;
                best_opp = opp_score;
                best_tiebreaker = tiebreaker;
            }
            my_pegs.pop_back();
        }

        unique_lock<mutex> lock(m);
        debug(thread_id, best_peg, best_score);
        if (best_my - best_opp > shared_best_score 
            || (best_my - best_opp == shared_best_score && best_tiebreaker < shared_best_tiebreaker)) {
            shared_best_score = best_my - best_opp;
            shared_best_peg = best_peg;
            shared_best_my = best_my;
            shared_best_opp = best_opp;
            shared_best_tiebreaker = best_tiebreaker;
        }
        shared_trials += trials;
    }

    int place_peg(int peg_idx = -1) {
        if (BOARD_HEIGHT > 20) {
            auto start_time = chrono::steady_clock::now();
            shared_best_peg = -1;
            shared_best_score = numeric_limits<int>::min();
            shared_best_my = -1;
            shared_best_opp = -1;
            shared_best_tiebreaker = numeric_limits<int>::max();
            shared_trials = 0;
            shared_idxs.resize(BOARD_CELLS, 0);
            iota(shared_idxs.begin(), shared_idxs.end(), 0);
            shuffle(shared_idxs.begin(), shared_idxs.end(), RNG);
            
            vector<thread> threads;
            const int block_size = (BOARD_CELLS - 1) / THREAD_COUNT + 1;
            for (int i = 0; i < THREAD_COUNT; i++) {
                const int left = i * block_size;
                const int right = min((i + 1) * block_size, BOARD_CELLS);
                threads.push_back(thread([this, i, left, right] { this->thread_fun(i, left, right); }));
            }
            for (int i = 0; i < THREAD_COUNT; i++) {
                threads[i].join();
            }
            pegs[MY_COLOR].push_back(shared_best_peg);
            auto end_time = chrono::steady_clock::now();
            auto diff = end_time - start_time;
            cout << chrono::duration <double, milli> (diff).count() << " ms" << nl;
            debug(peg_idx, shared_trials);
            debug(shared_best_peg, shared_best_score, shared_best_my, shared_best_opp);
            return shared_best_peg;
        }
        auto start_time = chrono::steady_clock::now();
        vector<int> my_pegs = pegs[MY_COLOR];
        vector<int> opp_pegs = pegs[OPP_COLOR];
        int best_peg = -1, best_score = numeric_limits<int>::min();
        int best_my = -1, best_opp = -1;
        int best_tiebreaker = numeric_limits<int>::max();
        for (int i = 0; i < BOARD_CELLS; ++i) {
            if (board[i] != 0) continue;
            my_pegs.push_back(i);
            int my_score = this->score(my_pegs, opp_pegs);
            int opp_score = this->score(opp_pegs, my_pegs);
            int tiebreaker = min(i / BOARD_WIDTH, BOARD_HEIGHT - 1 - i / BOARD_WIDTH)
                            + min(i % BOARD_WIDTH, BOARD_WIDTH - 1 - i % BOARD_WIDTH);
            if (my_score - opp_score > best_score 
                || (my_score - opp_score == best_score && tiebreaker < best_tiebreaker)) {
                best_score = my_score - opp_score;
                best_peg = i;
                best_my = my_score;
                best_opp = opp_score;
                best_tiebreaker = tiebreaker;
            }
            my_pegs.pop_back();
        }
        debug(peg_idx);
        debug(best_peg, best_score, best_my, best_opp);
        assert(best_peg != -1);
        pegs[MY_COLOR].push_back(best_peg);
        auto end_time = chrono::steady_clock::now();
        auto diff = end_time - start_time;
        cout << chrono::duration <double, milli> (diff).count() << " ms" << nl;
        return best_peg;
    }

	vector<int> place_rubberband(int band_idx = -1) {
        if (rubber_bands.size() == 0) {
            score(pegs[MY_COLOR], pegs[OPP_COLOR], true);
        }
        debug(band_idx, rubber_bands[band_idx]);
        return rubber_bands[band_idx];
	}
};

// Everything below here is game logic and socket handling

int socket_id;
struct sockaddr_in server_address;

void send_message(std::string& s) {
    send(socket_id, s.c_str(), s.length(), 0);
}

string receive_message(bool game_message = false) {
    const int sz = 1 << 14;
    // const int sz = game_message ? (1 << 20) : 2048;
    char message[sz];
	int idx = read(socket_id, message, sz);
    message[idx] = '\0';
	return message;
}

string trim(string& str) {
    str.erase(str.find_last_not_of(" \n\r\t") + 1);
    return str;
}

string rubberband_message(vector<int>& positions) {
    string message = "[";
    for (int i = 0; i < static_cast<int>(positions.size()); ++i) {
        message += to_string(positions[i]);
        if (i != static_cast<int>(positions.size()) - 1) {
            message += ", ";
        }
    }
    message += "]";
    return message;
}

// this function contains the main game loop
void play_game() {
    // send greeting
	send_message(BOT_NAME);

    // read initial data
	istringstream iss(receive_message(false));

    int board_height, board_width, peg_count, rubberband_count, color;
    iss >> board_height >> board_width >> peg_count >> rubberband_count >> color;
    assert(board_height <= 50);
    assert(peg_count <= 20);
    assert(rubberband_count <= 20);
    assert(board_height == board_width);
    assert(peg_count <= board_height / 2);
    assert(rubberband_count <= peg_count);
    Bot bot(board_height, board_width, peg_count, rubberband_count, color);
    const int board_cells = board_height * board_width;

    // place pegs
    for (int peg = 0; peg < peg_count; ++peg) {
        string board_str = receive_message(false);
        assert(board_str.front() == '[' && board_str.back() == ']');
        board_str = board_str.substr(1, board_str.length() - 2);
        istringstream tss(board_str);
        vector<int> board(board_cells, 0);
        string token;
        for (int i = 0; i < board_cells; ++i) {
            getline(tss, token, ',');
            token = trim(token);
            board[i] = stoi(token);
        }
        bot.update(board);

        string message = to_string(bot.place_peg(peg));
        send_message(message);
    }

    // place rubberbands
    for (int band = 0; band < rubberband_count; ++band) {
        string board_str = receive_message(false);
        assert(board_str.front() == '[' && board_str.back() == ']');
        board_str = board_str.substr(1, board_str.length() - 2);
        istringstream tss(board_str);
        vector<int> board(board_cells, 0);
        string token;
        for (int i = 0; i < board_cells; ++i) {
            getline(tss, token, ',');
            token = trim(token);
            board[i] = stoi(token);
        }
        bot.update(board);

        vector<int> positions = bot.place_rubberband(band);
        string message = rubberband_message(positions);
        send_message(message);
    }
}

// this function handles the socket connection process
void socket_connect(int port) {
	// create socket
	socket_id = socket(AF_INET, SOCK_STREAM, 0);
	if (socket_id < 0) {
		std::cout << "Error creating socket\n";
		exit(-1);
	}
	// set additional required connection info
	server_address.sin_family = AF_INET;
	server_address.sin_port = htons(port);
	// convert ip address to correct form
	inet_pton(AF_INET, "localhost", &server_address.sin_addr);
	// attempt connection
	if (connect(socket_id, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
		std::cout << "Connection failed\n";
		exit(-1);
	}
}

int main(int argc, char *argv[]) {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

	// port is an optional command line argument
	socket_connect(argc == 2 ? std::stoi(argv[1]) : 4000);

	// main game loop
	play_game();
	return 0;
}

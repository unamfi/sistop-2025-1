//Programa generado para la participación en un contest de programación competitiva
//de parte de CPCFI (Club de Programación Competitiva de la Facultad de Ingeniería)


/*El código resuelve el siguiente problema:
Rudolf and the Ugly String
Link: https://codeforces.com/group/TGNbtcQjJo/contest/550105/problem/E
*/

#include <bits/stdc++.h>
using namespace std;

void solve(){
    int n, count = 0;
    string s;
    cin >> n;
    cin >> s;
    vector<bool> e(n, false);

    for (int i = 0; i < n; i++) {
        if (i + 5 <= n) {
            if (s.substr(i, 5) == "mapie") {
                e[i + 2] = true;
                count++;
            }
        }

        if (i + 2 <= n) {
            if (s.substr(i, 3) == "map" || s.substr(i, 3) == "pie") {
                if (e[i] == true || e[i + 2] == true){
                    continue;
                } else {
                    e[i + 1] = true;
                    count++;
                }
            }
        }
    }

    cout << count << endl;
}

int main() {
    int t;
    cin >> t;

    while (t--) {
        solve();
    }
}
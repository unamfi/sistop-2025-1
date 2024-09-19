#include <bits/stdc++.h>
using namespace std;

int main(){
    int n;
    bool flag = false;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++){
        cin >> a[i];
    }

    sort(a.begin(), a.end(), greater<int>());

    for (int j = 0; j < n-2; j++){
        if(a[j] >= a[j+1] + a[j+2]){
            flag = true;
            continue;
        } else if(a[j] <= a[j+1] + a[j+2]){
            cout << "YES" << endl;
            flag = false;
            break;
        }
    }
    if(flag == true){
        cout << "NO" << endl;
    }
}
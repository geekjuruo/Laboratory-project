#include <iostream>
using namespace std;
int res[10000];
int solve(int a[], int lena, int b[], int lenb) {
    int num = 0;
    for(int i = 0 ; i < lena; i++) {
        for(int j = 0 ; j < lenb; j++) {
            if(a[i] == b[j]) {
                int flag = 0;
                for(int k = 0; k < num; k++) {
                    if(a[i] == res[k]) {
                        flag = 1;
                    }
                }
                if(flag == 0) {
                    res[num++] = a[i];
                }
            }
        }
    }
    return num;
}

int main() {
    int a[4];
    int b[6];
    for(int i = 0; i < 4; i++) {
        cin >> a[i];
    }
    for(int i = 0; i < 6; i++) {
        cin >> b[i];
    }
    int num = solve(a, 4, b, 6);
    for(int i = 0; i < num; i++) {
        cout << res[i] << " ";
    }
    return 0;
}
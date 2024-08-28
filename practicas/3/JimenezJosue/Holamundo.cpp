#include <iostream>
#include <string>
using namespace std;

int main(){
	string name;
	cout << "Por favor, ingresa tu nombre: ";
    getline(cin, name);
	cout << "Hola, " << name << "!" << std::endl;
	return 0;
}
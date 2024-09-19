#include<stdio.h>
#include<math.h>
#define e 0.0001

double f(double);

int main(){
	
	double xa, xb, m, xc; //intervalos
	
	printf("-----Metodos de Interpolacion-----\n");
	printf("Ingresa el intervalo Xa: ");
	scanf("%lf",&xa);
	printf("Ingresa el intervalo Xb: ");
	scanf("%lf",&xb);
	//Calculos
	int i=0; //Iteraciones 
	if(f(xa)*f(xb)>0){
		printf("Las raices no existen en el intervalo.\n");
	}else{
		while(e<fabs(xb - xa)){
			m=(f(xb)-f(xa))/(xb-xa);
			xc=xa-(f(xa)/m);
			if(f(xa)*f(xc)<0){
				xb=xc;
			}else{
				xa=xc;
			}
			i++;
		}
		
		printf("La raiz es: %.6lf\n", xc);
        printf("El numero de iteraciones es: %d\n", i);
		
	}
	return 0; 
}

double f(double x){
	return pow(x,2)+7*x-exp(x);
}
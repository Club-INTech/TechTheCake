#include <stdio.h>
#include <stdlib.h>

int main()
{
    FILE* serie = NULL;
    serie = fopen("/dev/ttyUSB0", "r+");
    if (serie != NULL)
    {
	printf("Ouverture réussie\n");
	
    fclose(serie);
	}
	else
	printf("Ouverture impossible\n");

    return 0;
}

int readUltrason() {
	char buffer[20];
    fprintf(serie, "s\r");
	fgets(buffer, 20, serie);
	printf("%s\n", buffer);

}

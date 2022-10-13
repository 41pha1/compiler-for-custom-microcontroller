int a = 1;
int b = 1;

while(a < 128)
{
    int temp = a;
    a = b;
    b = temp + b;
    print(a);
}
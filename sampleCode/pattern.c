int a;
int c = 0;

for(int j; 1; j = j)
{
  a = c;
  for(int i = 0; i < 8; i = i + 1)
  {
    display(i, a);
    a = a + a + 1;

    if(a >= 128)
    {
      a = a - 1;
    }
  }
  c = c + c + 1;
  if(c >= 128)
  {
    c = c - 1;
  }
}

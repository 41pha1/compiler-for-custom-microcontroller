int cells[64];
int nextCells[64];
int neighbour_offsets[8];

for(int i = 0; i < 64; i = i + 1)
{
  cells[i] = false;
}

cells[1] = true;
cells[10] = true;
cells[16] = true;
cells[17] = true;
cells[18] = true;

neighbour_offsets[0] = -9;
neighbour_offsets[1] = -8;
neighbour_offsets[2] = -7;
neighbour_offsets[3] = -1;
neighbour_offsets[4] = 1;
neighbour_offsets[5] = 7;
neighbour_offsets[6] = 8;
neighbour_offsets[7] = 9;

int index = 0;
for(int x = 0; x < 8; x = x + 1)
{
  int line = 0;
  for(int y = 0; y < 8; y = y + 1)
  {
    line = line + line;
    if(cells[index])
      line = line + 1;
    index = index + 1;
  }
  display(x, line);
}

while(true)
{
  index = 0;
  for(int x = 0; x < 8; x = x + 1)
  {
    for(int y = 0; y < 8; y = y + 1)
    {
      print(index);
      int n = 0;

      for(int i = 0; i < 8; i = i + 1)
      {
        int ni = neighbour_offsets[i] + index;
        if(ni & 7 == 7 && x == 0)
          ni = ni + 8;
        if(ni & 7 == 0 && x == 7)
          ni = ni - 8;
        if(ni > 128)
          ni = ni + 64;
        if(ni > 63)
          ni = ni - 64;
        n = n + cells[ni];
      }

      nextCells[index] = (n == 3));

      if(n == 2)
        nextCells[index] = cells[index];

      index = index + 1;
    }
  }
  index = 0;
  for(int x = 0; x < 8; x = x + 1)
  {
    int line = 0;
    for(int y = 0; y < 8; y = y + 1)
    {
      line = line + line;
      cells[index] = nextCells[index];
      if(cells[index])
        line = line + 1;
      index = index + 1;
    }
    display(x, line);
  }
}

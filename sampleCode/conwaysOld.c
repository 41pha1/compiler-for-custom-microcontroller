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

neighbour_offsets[0] = 247;
neighbour_offsets[1] = 248;
neighbour_offsets[2] = 249;
neighbour_offsets[3] = 255;
neighbour_offsets[4] = 1;
neighbour_offsets[5] = 7;
neighbour_offsets[6] = 8;
neighbour_offsets[7] = 9;

while(true)
{
  int index = 0;
  for(int x = 0; x < 8; x = x + 1)
  {
    for(int y = 0; y < 8; y = y + 1)
    {
      print(index);
      int n = 0;

      for(int i = 0; i < 8; i = i + 1)
      {
        int ni = neighbour_offsets[i] + index;
      }

      for(int i = 0; i < 3; i = i + 1)
      {
        int xi = x+i-1;
        if(xi == 255)
          xi = xi + 8;
        if(xi == 8)
          xi = xi - 8;

        for(int j = 0; j < 3; j = j + 1)
        {
          int yi = y+j-1;
          if(yi == 255)
            yi = yi + 8;
          if(yi == 8)
            yi = yi - 8;

          int ni = yi;

          for(int k = 0; k < 8; k = k + 1)
            ni = ni + xi;

          if(cells[ni])
            n = n + 1;
        }
      }
      if(cells[index])
      {
        n = n - 1;
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
      if(cells[index])
        line = line + 1;
      cells[index] = nextCells[index];
      index = index + 1;
    }
    display(x, line);
  }
}

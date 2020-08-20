#include <stdio.h>

int getByte(int x, int n) {
  int mask=0xff;
  return (x>>(n<<3))&mask;
}

int main()
{
    int ans = getByte(0x12345678, 1);
    int a = 3;
    int *p;
    p = &a;
    
    printf("ans = %#x\n", ans);
    printf("%#x\n", (0x12345678>>8));
    printf("*p = %d\n", *p);
    printf("p = %d\n", p);
    printf("&a = %d\n", &a);
}
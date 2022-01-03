#include <stdio.h>
#include <stdint.h>
#include <Windows.h>
#include "VmCode.h"

#define NOR_UINT16(A, B) (~(A | B)) & 0xFFFF

#define reg_ip          0
#define reg_shift       1
#define reg_sp          2
#define reg_out_value   3
#define reg_out_int     4
#define reg_in_value    5
#define reg_in_int      6
#define reg_z           7
#define reg_zero_flag   8
#define reg_carry_flag  9

uint16_t* g_mem = NULL;
unsigned char* g_fileData = vmCode;
size_t g_fileDataSize = sizeof(vmCode);

//Password: WE1rd_v1R7UaL_M@chINE_Ev3R
bool vm_init()
{
    g_mem = (uint16_t*)VirtualAlloc(NULL, 65536 * sizeof(uint16_t), MEM_COMMIT, PAGE_READWRITE);
    if (g_mem == NULL)
        return false;

    //Init segment
    //stack segment: 20 - 200
    //program segment: 300 - 65535

    memcpy(&g_mem[300], g_fileData, g_fileDataSize);

    g_mem[reg_ip] = 300;

    return true;
}

bool vm_run()
{
    while (g_mem[reg_ip] != 0xFFFF)
    {
        if (g_mem[reg_out_int] == 1)
        {
            g_mem[reg_out_int] = 0;
            printf("%c", g_mem[reg_out_value]);
        }

        if (g_mem[reg_in_int] == 1)
        {
            g_mem[reg_in_int] = 0;
            scanf("%c", (char*)&g_mem[reg_in_value]);
        }

        uint16_t sp = g_mem[reg_ip];
        uint16_t a = g_mem[sp];
        uint16_t b = g_mem[sp + 1];
        uint16_t r = g_mem[sp + 2];
        g_mem[reg_ip] += 3;

        uint16_t f = NOR_UINT16(g_mem[a], g_mem[b]);
        g_mem[r] = f;
        g_mem[reg_shift] = ((f >> 15) & 1) | ((f & 0x7FFF) << 1); //ROL f, 1
    }
    return true;
}

bool vm_free()
{
    if (g_mem)
    {
        VirtualFree(g_mem, 0, MEM_RELEASE);
        g_mem = NULL;
    }
    return true;
}

int main(int argc, char* argv[])
{
    if (!vm_init())
    {
        printf("Failed to init program\n");
        return 0;
    }
    if (!vm_run())
        printf("Failed to run program\n");

    vm_free();

    return 0;
}
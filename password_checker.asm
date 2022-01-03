printc char_P
printc char_a
printc char_s
printc char_s
printc char_w
printc char_o
printc char_r
printc char_d
printc char_colon
scanc pass_1
scanc pass_2
scanc pass_3
scanc pass_4
xor pass_1, char_t, tmp_value
or tmp_value, check_value, check_value
xor pass_2, char_e, tmp_value
or tmp_value, check_value, check_value
xor pass_3, char_s, tmp_value
or tmp_value, check_value, check_value
xor pass_4, char_t, tmp_value
or tmp_value, check_value, check_value
is_0 check_value
jz correct
printc char_w
printc char_r
printc char_o
printc char_n
printc char_g
exit
correct:
printc char_c
printc char_o
printc char_r
printc char_r
printc char_e
printc char_c
printc char_t
exit

char_H:
db 72
char_e:
db 101
char_l:
db 108
char_o:
db 111
char_space:
db 32
char_f:
db 102
char_r:
db 114
char_m:
db 109
char_n:
db 110
char_a:
db 97
char_c:
db 99
char_h:
db 104
char_i:
db 105
char_P:
db 80
char_s:
db 115
char_w:
db 119
char_d:
db 100
char_t:
db 116
char_g:
db 103
char_colon:
db 58


pass_1:
db 0
pass_2:
db 0
pass_3:
db 0
pass_4:
db 0

check_value:
db 0

tmp_value:
db 0

printc char_P
printc char_a
printc char_s
printc char_s
printc char_w
printc char_o
printc char_r
printc char_d
printc char_colon
jmp scan_password

check_value:
db 0

scan_password:
scanc pass_0
scanc pass_1
scanc pass_2
scanc pass_3
scanc pass_4
scanc pass_5
scanc pass_6
scanc pass_7
scanc pass_8
scanc pass_9
scanc pass_10
scanc pass_11
scanc pass_12
scanc pass_13
scanc pass_14
scanc pass_15
scanc pass_16
scanc pass_17
scanc pass_18
scanc pass_19
scanc pass_20
scanc pass_21
scanc pass_22
scanc pass_23
scanc pass_24
scanc pass_25

xor pass_0, const_87, tmp_value
or tmp_value, check_value, check_value

xor pass_1, pass_0, tmp_value
xor tmp_value, const_18, tmp_value
or tmp_value, check_value, check_value

xor pass_2, const_18, tmp_value
xor tmp_value, const_35, tmp_value
or tmp_value, check_value, check_value

xor pass_3, pass_2, tmp_value
xor tmp_value, const_67, tmp_value
or tmp_value, check_value, check_value

xor pass_4, const_67, tmp_value
xor tmp_value, const_39, tmp_value
or tmp_value, check_value, check_value

rol pass_5, tmp_value
xor tmp_value, const_190, tmp_value
or tmp_value, check_value, check_value

rol pass_6, tmp_value
xor tmp_value, const_236, tmp_value
or tmp_value, check_value, check_value

ror pass_7, tmp_value
xor tmp_value, const_32792, tmp_value
or tmp_value, check_value, check_value

xor pass_8, const_32792, tmp_value
xor tmp_value, const_32842, tmp_value
or tmp_value, check_value, check_value

xor pass_9, pass_7, tmp_value
xor tmp_value, const_6, tmp_value
or tmp_value, check_value, check_value

xor pass_10, pass_8, tmp_value
xor tmp_value, const_7, tmp_value
or tmp_value, check_value, check_value

xor pass_11, char_a, tmp_value
or tmp_value, check_value, check_value

xor pass_12, const_87, tmp_value
xor tmp_value, const_27, tmp_value
or tmp_value, check_value, check_value

xor pass_13, pass_5, tmp_value
or tmp_value, check_value, check_value

ror pass_14, tmp_value
xor tmp_value, const_32806, tmp_value
or tmp_value, check_value, check_value

add pass_15, const_32806, tmp_value
xor tmp_value, const_32870, tmp_value
or tmp_value, check_value, check_value

xor pass_16, pass_15, tmp_value
xor tmp_value, const_35, tmp_value
or tmp_value, check_value, check_value

xor pass_17, const_32870, tmp_value
xor tmp_value, const_32782, tmp_value
or tmp_value, check_value, check_value

ror pass_18, tmp_value
xor tmp_value, const_32804, tmp_value
or tmp_value, check_value, check_value

xor pass_19, pass_18, tmp_value
xor tmp_value, const_7, tmp_value
or tmp_value, check_value, check_value

xor pass_20, const_32804, tmp_value
xor tmp_value, const_32865, tmp_value
or tmp_value, check_value, check_value

xor pass_21, pass_13, tmp_value
or tmp_value, check_value, check_value

ror pass_22, tmp_value
xor tmp_value, const_32802, tmp_value
or tmp_value, check_value, check_value

xor pass_23, const_32802, tmp_value
xor tmp_value, const_32852, tmp_value
or tmp_value, check_value, check_value

ror pass_24, tmp_value
xor tmp_value, const_32793, tmp_value
or tmp_value, check_value, check_value

xor pass_25, const_32793, tmp_value
xor tmp_value, const_32843, tmp_value
or tmp_value, check_value, check_value

is_0 check_value
jz correct


wrong:
printc char_W
printc char_r
printc char_o
printc char_n
printc char_g
exit

correct:
printc char_T
printc char_e
printc char_t
printc char_C
printc char_T
printc char_F
printc char_open
printc pass_0
printc pass_1
printc pass_2
printc pass_3
printc pass_4
printc pass_5
printc pass_6
printc pass_7
printc pass_8
printc pass_9
printc pass_10
printc pass_11
printc pass_12
printc pass_13
printc pass_14
printc pass_15
printc pass_16
printc pass_17
printc pass_18
printc pass_19
printc pass_20
printc pass_21
printc pass_22
printc pass_23
printc pass_24
printc pass_25
printc char_close
exit

tmp_value:
db 0

const_87:
db 87
const_18:
db 18
const_35:
db 35
const_67:
db 67
const_39:
db 39
const_190:
db 190
const_236:
db 236
const_32792:
db 32792
const_32842:
db 32842
const_32806:
db 32806
const_6:
db 6
const_7:
db 7
const_27:
db 27
const_32870:
db 32870
const_32782:
db 32782
const_32804:
db 32804
const_32865:
db 32865
const_32802:
db 32802
const_32852:
db 32852
const_32793:
db 32793
const_32843:
db 32843

pass_0:
db 0
pass_1:
db 0
pass_2:
db 0
pass_3:
db 0
pass_4:
db 0
pass_5:
db 0
pass_6:
db 0
pass_7:
db 0
pass_8:
db 0
pass_9:
db 0
pass_10:
db 0
pass_11:
db 0
pass_12:
db 0
pass_13:
db 0
pass_14:
db 0
pass_15:
db 0
pass_16:
db 0
pass_17:
db 0
pass_18:
db 0
pass_19:
db 0
pass_20:
db 0
pass_21:
db 0
pass_22:
db 0
pass_23:
db 0
pass_24:
db 0
pass_25:
db 0

char_r:
db 114
char_o:
db 111
char_a:
db 97
char_P:
db 80
char_s:
db 115
char_w:
db 119
char_W:
db 87
char_d:
db 100
char_t:
db 116
char_g:
db 103
char_T:
db 84
char_colon:
db 58
char_C:
db 67
char_F:
db 70
char_e:
db 101
char_open:
db 123
char_close:
db 125
char_n:
db 110
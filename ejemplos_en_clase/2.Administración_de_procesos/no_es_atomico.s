	.file	"no_es_atomico.c"
	.text
	.globl	x
	.bss
	.align 4
	.type	x, @object
	.size	x, 4
x:
	.zero	4
	.globl	y
	.align 4
	.type	y, @object
	.size	y, 4
y:
	.zero	4
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$0, x(%rip)
	movl	$1, y(%rip)
	movl	x(%rip), %eax
	addl	$2, %eax
	movl	%eax, x(%rip)
	movl	y(%rip), %edx
	movl	%edx, %eax
	addl	%eax, %eax
	addl	%edx, %eax
	movl	%eax, y(%rip)
	movl	x(%rip), %edx
	movl	y(%rip), %eax
	addl	%edx, %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (Debian 14.2.0-4) 14.2.0"
	.section	.note.GNU-stack,"",@progbits

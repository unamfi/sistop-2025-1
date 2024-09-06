	.file	"hola_mundo.c"
	.text
	.section	.rodata
	.align 8
.LC0:
	.string	"\302\241Hola mundo!\n\n...Mundo inmundo...\n"
	.align 8
.LC1:
	.string	"Tengo un arreglo de 50 enteros en la direcci\303\263n de memoria: %x\n"
	.text
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$16, %rsp
	leaq	.LC0(%rip), %rax
	movq	%rax, %rdi
	call	puts@PLT
	movl	$200, %edi
	call	malloc@PLT
	movq	%rax, -8(%rbp)
	movq	-8(%rbp), %rax
	movq	%rax, %rsi
	leaq	.LC1(%rip), %rax
	movq	%rax, %rdi
	movl	$0, %eax
	call	printf@PLT
	nop
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"GCC: (Debian 13.3.0-1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits

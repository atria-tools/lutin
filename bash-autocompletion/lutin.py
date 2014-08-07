_lutin() 
{
	local cur prev optshorts opts renameprev listmodule
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	optshorts="-h -v -C -f -P -j -s -t -c -m -r -p"
	opts="--help --verbose --color --force --pretty --jobs --force-strip --target --compilator --mode --prj --package --simulation"
	
	renameprev=${prev}
	case "${renameprev}" in
		-h)
			renameprev="--help"
			;;
		-v)
			renameprev="--verbose"
			;;
		-C)
			renameprev="--color"
			;;
		-f)
			renameprev="--force"
			;;
		-P)
			renameprev="--pretty"
			;;
		-j)
			renameprev="--jobs"
			;;
		-s)
			renameprev="--force-strip"
			;;
		-t)
			renameprev="--target"
			;;
		-c)
			renameprev="--compilator"
			;;
		-m)
			renameprev="--mode"
			;;
		-r)
			renameprev="--prj"
			;;
		-p)
			renameprev="--package"
			;;
	esac
	#
	#  Complete the arguments to some of the basic commands.
	#
	case "${renameprev}" in
		--compilator)
			local names="clang gcc"
			COMPREPLY=( $(compgen -W "${names}" -- ${cur}) )
			return 0
			;;
		--jobs)
			local names="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
			COMPREPLY=( $(compgen -W "${names}" -- ${cur}) )
			return 0
			;;
		--target)
			local names=`lutin.py --list-target`
			COMPREPLY=( $(compgen -W "${names}" -- ${cur}) )
			return 0
			;;
		--mode)
			local names="debug release"
			COMPREPLY=( $(compgen -W "${names}" -- ${cur}) )
			return 0
			;;
		*)
		;;
	esac
	
	if [[ ${cur} == --* ]] ; then
		COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
		return 0
	fi
	if [[ ${cur} == -* ]] ; then
		COMPREPLY=( $(compgen -W "${optshorts}" -- ${cur}) )
		return 0
	fi
	listmodule=`lutin.py --list-module`
	COMPREPLY=( $(compgen -W "${listmodule}" -- ${cur}) )
	return 0
}

complete -F _lutin lutin.py
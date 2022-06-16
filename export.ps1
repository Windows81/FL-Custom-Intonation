$t = @{
	523.251 = "~523.251 Hz [C♮]"
	400.000 = "400 Hz [G+]"
	432.000 = "432 Hz [A−]"
	440.000 = "440 Hz [A♮"
	480.000 = "480 Hz [B−]"
	500.000 = "500 Hz [B+]"
	512.000 = "512 Hz [C−]"
	576.000 = "576 Hz [D−]"
	600.000 = "600 Hz [D+]"
	640.000 = "640 Hz [E−]"
	672.000 = "672 Hz [E+]"
	720.000 = "720 Hz [F+]"
	768.000 = "768 Hz [G−]"
}

foreach ($i in $t.GetEnumerator()) {
	$k = $i.Value;
	$o = [math]::log2($i.Key / 440) * 12 - 3;
	$f = "~/Documents/Image-Line/FL Studio/Presets/Plugin presets/Effects/Control Surface/Scala/$k";
	mkdir $f -ErrorAction Ignore;
	ls $PSScriptRoot/scl/* | % {
		py $PSScriptRoot/add_scale.py -o $o --fst-file "$f/{}.fst" $_.FullName
	}
}

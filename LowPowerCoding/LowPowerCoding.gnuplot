reset
set zero 0.0
set term svg enhanced size 800,600 lw 1 font "Times New Roman,20"
set output "P.svg"
set ticslevel 0
set xlabel "N_{w}"
set ylabel "P_{a3} / P_{a2}"
set xrange [2. : 1024.]
set yrange [0. : 4.]
set logscale xy 2
plot \
  4/(log(x)/log(2)) \
   notitle

reset
set zero 0.0
set term svg enhanced size 800,600 lw 1 font "Times New Roman,20"
set output "R.svg"
set palette rgb 33,13,10
set xlabel "N_{w}"
set ylabel "T_{0} / T_{s}"
set cblabel "R_{3} / R_{2}"
set xrange [2. : 1024.]
set yrange [0.015625 : 1.]
set cbrange[0.125 : 8]
set isosamples 256
set pm3d map
set logscale xycb 2
splot \
  (log(x)/log(2)) / (1+(y)*(x-2)/4)

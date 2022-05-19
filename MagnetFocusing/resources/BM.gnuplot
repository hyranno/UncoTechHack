reset
set zero 0.0
# set term postscript eps color solid lw 2 size 16.4 cm, 12.3 cm font ",24"
# set output "BM.eps"
set term svg enhanced size 800,600 lw 1 font ",20"
set output "BM.svg"
set palette rgb 33,13,10
set view 90.0, 90.0
set view equal xyz
set ticslevel 0
set xlabel "x"
set ylabel "y"
set zlabel "z"
set xrange [-20.     : 20.    ]
set yrange [-20.     : 20.    ]
set zrange [-20.     : 20.    ]
set cbrange[0 : 15]
unset xlabel
unset xzeroaxis
unset xtics
min(v1, v2) = ((v1<v2)? v1 : v2)
len(x,y,z) = sqrt(x**2+y**2+z**2)
splot \
  "BMabs.dat" \
    using 1:2:3:4 with pm3d title "B,M (yz-plane)", \
  "M.dat" \
    using 1:2:3:($4/len($4,$5,$6)):($5/len($4,$5,$6)):($6/len($4,$5,$6)) \
    every 2:2 with vectors linecolor rgb "#ffffff" title "", \
  "B.dat" \
    using 1:2:3:($4/len($4,$5,$6)):($5/len($4,$5,$6)):($6/len($4,$5,$6)) \
    every 2:1 with vectors linecolor rgb "#000000" title ""

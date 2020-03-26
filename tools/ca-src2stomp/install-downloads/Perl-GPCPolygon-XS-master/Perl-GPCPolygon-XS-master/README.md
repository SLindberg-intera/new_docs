Perl-GPCPolygon-XS-
===================

This is a modification of Math::Geometry::Planar::GPC::Polygon without using Inline::C

Author of Math::Geometry::Planar::GPC::Polygon - Eric L. Wilhelm

Modified by Alexei Kasatkin ( removed Inline::C dependence, updated GPC, introduced XS-file )
3 functions that use non-Perl types were stripped to simplify conversion.

BE CAREFUL AND CHECK FOR MEMORY LEAKS - I HAVE NO IDEA ABOUT PERL MEMORY MANAGEMENT :)

    This module and its C source code (functions.c) are distributed under
    the same terms as Perl. See the Perl source package for details.

    You may use this software under one of the following licenses:

      (1) GNU General Public License
        (found at http://www.gnu.org/copyleft/gpl.html)
      (2) Artistic License
        (found at http://www.perl.com/pub/language/misc/Artistic.html)

    The General Polygon Clipping library (gpc.c and gpc.h) is distributed as
    "free for non-commercial use". See gpc.c for details. A copy of these
    files has been included with this distribution strictly for convenience
    purposes, but YOU ARE RESPONSIBLE FOR ADHERING TO BOTH THE GPC LICENSE
    AND THE LICENSE OF THIS MODULE. Note that the C library is authored by
    Alan Murta.

    You may want to check the GPC home page for a more current version:

      http://www.cs.man.ac.uk/aig/staff/alan/software/



using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace stomp_extrap_modflow.data
{
    class datafile
    {
        public datafile()
        {
            radius = 0;
        }
        public double year { get; set; }
        public double radius { get; set; }
        public double concentration { get; set; }
    }
}

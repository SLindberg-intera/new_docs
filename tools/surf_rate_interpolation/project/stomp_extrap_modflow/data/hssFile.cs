using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace stomp_extrap_modflow.data
{
    class hssFile
    {
        public hssFile()
        {
            faclength = 1;
            factime = 1;
            facmass = 1;
            RunOption = "NoRunHSSM";
        }
        public string comment { get; set; }
        public int MaxHSSSource { get; set; }
        public int MaxHSSCells { get; set; }
        public int MaxHSSStep { get; set; }
        public string RunOption { get; set; }
        public int faclength { get; set; }
        public int factime { get; set; }
        public int facmass { get; set; }
        public int nHSSSource { get; set; }        
    }
}

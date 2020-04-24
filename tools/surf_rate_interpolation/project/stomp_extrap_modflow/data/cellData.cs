using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace stomp_extrap_modflow.data
{
    class cellData
    {
        public string HSSFileName { get; set; }
        public string inHSSFile { get; set; }
        public string kSource { get; set; }
        public string iSource { get; set; }
        public string jSource { get; set; }
        public string SourceName { get; set; }
        public string iHSSComp { get; set; }
    }
}

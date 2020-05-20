using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;
namespace stomp_extrap_modflow.data
{
    class hss_data_files : INotifyPropertyChanged
    {
        public hss_data_files()
        {
            id = 1;
            k = "1";
        }
        public int id { get; set; }
        public bool time { get; set; }
        public string source { get; set; }
        public string name { get; set; }
        public string i { get; set; }
        public string j { get; set; }
        public string k { get; set; }
        public int col { get; set; }
        public event PropertyChangedEventHandler PropertyChanged;
    }
}

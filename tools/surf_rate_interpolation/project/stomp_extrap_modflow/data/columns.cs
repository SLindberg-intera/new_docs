using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using System.ComponentModel;
namespace stomp_extrap_modflow.data
{
    class columns : INotifyPropertyChanged
    {
        public int column_num { get; set; }
        public string title { get; set; }
        public string definition { get; set; }
        public bool time { get; set; }
        public decimal conv_factor { get; set; }
        public event PropertyChangedEventHandler PropertyChanged;
    }
}

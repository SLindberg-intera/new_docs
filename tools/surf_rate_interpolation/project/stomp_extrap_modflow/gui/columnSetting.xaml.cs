using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using stomp_extrap_modflow.data;

namespace stomp_extrap_modflow.gui
{
    /// <summary>
    /// Interaction logic for columnSetting.xaml
    /// </summary>
    public partial class columnSetting : Page
    {
        internal List<columns> column_def;
        public columnSetting()
        {
            InitializeComponent();
            column_def = new List<columns>();
            this.DataContext = column_def;
            //this.tb_instructions.Text = instructions;
        }
        public void refresh()
        {
            DataContext = column_def;
            auGrid.Items.Refresh();
        }
        private string instructions =
@"The Header grid allows the user to define which columns to utilize.  The columns are listed below with descriptions:
  -Column: The order the columns are in. read only
  -Time: Marks the column that the time(such as year) is found.
     --Make sure Definition reflects the correct unit; currently only 
       'year' is supported.
  -title: title of the column from the original file, what line the 
          headers start on is pulled from the 'header1 row' and 
          'header2 row' fields.
  -definition: this is where you define your data.
     --empty/null: means skip this column
     --user defined word/COPC/etc: Defines the column to be used.  if 
       multiple columns have the same definition they will be added 
       together to form a single column in the output. If you have 
       multiple columns with different names the application will 
       output a file for each unique name.
  -Conv. F.: This is factor used to convert between units.  If the 
       original data is in g and you need it in Ci then you would put 
       the multiplier here.  IE for Tc-99 to go from g to ci you would 
       multiple the g by .017, therefor you would put .017 in this field.
    --Special note, if column is marked as Time, then it will be assumed 
      that the conv. F. is to be added to the year.  This is normally used 
      when the data does not have a starting year, IE it starts at 0 and 
      increments from there, instead of starting at 1942 for example.
* If Processing multiple files each file will need to have the same column structure.
** Output files will be named using the input file name with the unique definition name added to the end of the file.
";

        private void button_Click(object sender, RoutedEventArgs e)
        {

            MessageBox.Show(instructions, "Info");
        }
    }

}

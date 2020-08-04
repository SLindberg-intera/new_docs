using System;
//using System.Collections.Generic;
//using System.Linq;
//using System.Text;
//using System.Threading.Tasks;
//using System.Windows;
using System.Windows.Controls;
using System.Text.RegularExpressions;
namespace surf_rate_interp.gui
{
    public class DataGriddecimalColumn : DataGridTextColumn
    {
        private static readonly Regex _regex = new Regex(@"^[-+]?[0-9]*\.?[0-9]?$");
        protected override object PrepareCellForEdit(System.Windows.FrameworkElement editingElement, System.Windows.RoutedEventArgs editingEventArgs)
        {
            TextBox edit = editingElement as TextBox;
            edit.PreviewTextInput += OnPreviewTextInput;

            return base.PrepareCellForEdit(editingElement, editingEventArgs);
        }
        private static bool IsTextAllowed(string text)
        {
            return !_regex.IsMatch(text);
        }

        void OnPreviewTextInput(object sender, System.Windows.Input.TextCompositionEventArgs e)
        {
            e.Handled = IsTextAllowed(e.Text);
            //try
            //{
            //    Convert.Todecimal(e.Text);
            //}
            //catch
            //{
            //    // Show some kind of error message if you want

            //    // Set handled to true
            //    e.Handled = true;
            //}
        }
    }
}

using System;
using System.Collections.Generic;
using Android.App;
using Android.Content;
using Android.Runtime;
using Android.Views;
using Android.Widget;
using Android.OS;
using Android.Support.Wearable.Views;
using Android.Support.V4.App;
using Android.Support.V4.View;
using Java.Interop;
using Android.Views.Animations;
using System.Net;
using System.Threading.Tasks;
using System.IO;
using System.Json;

namespace weartesr
{
    [Activity(Label = "weartesr", MainLauncher = true, Icon = "@drawable/icon")]
    public class MainActivity : Activity
    {
        int count = 1;

        protected override void OnCreate(Bundle bundle)
        {
            base.OnCreate(bundle);

            // Set our view from the "main" layout resource
            //SetContentView(Resource.Layout.Main);

            var layout = new LinearLayout(this) { Orientation = Orientation.Vertical };

            //var exceptionBox = FindViewById<TextView>(Resource.Id.textViewException);
            TextView exceptionBox = new TextView(this)
            {
                Text = "Exception: <None>",
                TextSize = 0.5f
            };

            try
            {
                AutoCompleteTextView apiUriTextView = new AutoCompleteTextView(this)
                {
                    Text = "http://greenhouse01.iot.oh.wsh.no:8080/api"
                };
                layout.AddView(apiUriTextView);
                //TODO: add connect button?

                Button buttonConnect = new Button(this) { Text = "Connect" };
                buttonConnect.Click += async (sender, e) =>
                {
                    await FetchApiLayout(apiUriTextView.Text, layout, exceptionBox);
                };
                layout.AddView(buttonConnect);
            }
            catch (Exception ex)
            {
                exceptionBox.Text = ex.ToString();
            }

            layout.AddView(exceptionBox);
            SetContentView(layout);
        }
        
        // Gets weather data from the passed URL.
        private async Task<JsonValue> FetchApiAsync(string url, TextView exceptionBox)
        {
            //var exceptionBox = FindViewById<TextView>(Resource.Id.textViewException);

            try
            {
                // Create an HTTP web request using the URL:
                HttpWebRequest request = (HttpWebRequest) HttpWebRequest.Create(new Uri(url));
                request.ContentType = "application/json";
                request.Method = "GET";

                // Send the request to the server and wait for the response:
                using (WebResponse response = await request.GetResponseAsync())
                {
                    // Get a stream representation of the HTTP web response:
                    using (Stream stream = response.GetResponseStream())
                    {
                        // Use this stream to build a JSON document object:
                        //JsonValue jsonDoc = await Task.Run(() => JsonObject.Load(stream));
                        JsonValue jsonDoc = JsonValue.Load(stream);
                        Console.Out.WriteLine("Response: {0}", jsonDoc.ToString());

                        // Return the JSON document:
                        return jsonDoc;
                    }
                }
            }
            catch (Exception ex)
            {
                exceptionBox.Text = ex.ToString();
                var empty = new JsonObject {{"value", new JsonPrimitive("")}};
                return empty;
            }
        }

        private async Task<bool> FetchApiLayout(string baseUri, LinearLayout layout, TextView exceptionBox)
        {
            try
            {
                JsonValue value = await FetchApiAsync(baseUri + "?class", exceptionBox);
                foreach (KeyValuePair<string, JsonValue> kvp in value)
                {
                    string cls = kvp.Value["class"];
                    string uri = baseUri + "/" + kvp.Key.Replace(".", "/") + "/";
                    if (cls.EndsWith("Led"))
                    {
                        ToggleButton toggle = new ToggleButton(this)
                        {
                            TextOn = kvp.Key.Replace("_", " ") + " off",
                            TextOff = kvp.Key.Replace("_", " ") + " on"
                        };
                        toggle.Click += async (sender, e) =>
                        {
                            if (((ToggleButton) sender).Checked)
                            {
                                JsonValue json1 = await FetchApiAsync(uri + "on", exceptionBox);
                            }
                            else
                            {
                                JsonValue json1 = await FetchApiAsync(uri + "off", exceptionBox);
                            }
                        };

                        JsonValue json = await FetchApiAsync(uri + "state", exceptionBox);
                        toggle.Checked = json["value"].ToString().Equals("1");
                        layout.AddView(toggle);
                    }
                    else if (cls.EndsWith("Dht11"))
                    {
                        Button buttonMeasure = new Button(this)
                        {
                            Text = kvp.Key.Replace("_", " ") + " measure"
                        };
                        TextView textViewTemperature = new TextView(this)
                        {
                            Text = "Temperature: <None>"
                        };
                        TextView textViewHumidity = new TextView(this)
                        {
                            Text = "Humidity: <None>"
                        };
                        buttonMeasure.Click += async (sender, e) =>
                        {
                            try
                            {
                                JsonValue dhtValue = await FetchApiAsync(uri + "value", exceptionBox);
                                string val = dhtValue["value"];
                                string[] vals = val.Split(new[] { 'c' }, 2);
                                if (vals.Length == 2)
                                {
                                    textViewTemperature.Text = "Temperature: " + vals[0] + "C";
                                    textViewHumidity.Text = "Humidity: " + vals[1] + "%";
                                }
                            }
                            catch (Exception ex)
                            {
                                exceptionBox.Text = ex.ToString();
                            }
                            /*
                            JsonValue temperature = await FetchApiAsync(uri + "temperature", exceptionBox);
                            textViewTemperature.Text = "Temperature: " + temperature["value"];

                            JsonValue humidity = await FetchApiAsync(uri + "humidity", exceptionBox);
                            textViewHumidity.Text = "Humidity: " + humidity["value"];
                            */
                        };
                        layout.AddView(buttonMeasure);
                        layout.AddView(textViewTemperature);
                        layout.AddView(textViewHumidity);
                    }
                    else if (cls.EndsWith("Adc"))
                    {
                        Button buttonAdc = new Button(this)
                        {
                            Text = cls + " - get ADC value"
                        };
                        TextView textViewAdc = new TextView(this)
                        {
                            Text = "Value: <None>"
                        };

                        buttonAdc.Click += async (sender, e) =>
                        {
                            JsonValue adcValue = await FetchApiAsync(uri + "read", exceptionBox);
                            textViewAdc.Text = "Value: " + adcValue["value"].ToString();
                        };

                        layout.AddView(buttonAdc);
                        layout.AddView(textViewAdc);
                    }
                    else if (cls.EndsWith("Door"))
                    {
                        foreach (JsonObject method in kvp.Value["methods"])
                        {
                            string name = method["name"].ToString().Replace("\"", "");
                            string methodUri = baseUri + "/" + name;
                            //.Replace("api", "root") //TODO: this is a bug

                            Button button = new Button(this)
                            {
                                Text = "Open " + name
                            };
                            button.Click += async (sender, e) =>
                            {
                                JsonValue json1 = await FetchApiAsync(methodUri, exceptionBox);
                            };

                            layout.AddView(button);
                        }
                    }

                }
            }
            catch (Exception ex)
            {
                exceptionBox.Text = ex.ToString();
            }
            return true;
        }

    }
}

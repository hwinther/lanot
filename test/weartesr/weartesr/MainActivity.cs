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
                    Text = "http://192.168.1.188:8080/api"
                };
                layout.AddView(apiUriTextView);
                //TODO: add connect button?

                Button buttonConnect = new Button(this) { Text = "Connect" };
                buttonConnect.Click += async (sender, e) =>
                {
                    await FetchApiLayout(apiUriTextView.Text, layout, exceptionBox);
                };
                layout.AddView(buttonConnect);

                /*
                var aLabel = new TextView(this) {Text = "Hello, World!!!"};

                var aButton = new Button(this) {Text = "Say Hello!"};

                aButton.Click += (sender, e) =>
                {
                    aLabel.Text = "Hello Android!";
                };

                layout.AddView(aLabel);
                layout.AddView(aButton);
                */

                /*
                var v = FindViewById<WatchViewStub>(Resource.Id.watch_view_stub);
                v.LayoutInflated += delegate
                {
                // Get our button from the layout resource,
                // and attach an event to it
                Button button = FindViewById<Button>(Resource.Id.myButton);

                    button.Click += delegate
                    {
                        var notification = new NotificationCompat.Builder(this)
                            .SetContentTitle("Button tapped")
                            .SetContentText("Button tapped " + count++ + " times!")
                            .SetSmallIcon(Android.Resource.Drawable.StatNotifyVoicemail)
                            .SetGroup("group_key_demo").Build();

                        var manager = NotificationManagerCompat.From(this);
                        manager.Notify(1, notification);
                        button.Text = "Check Notification!";
                    };

                    ToggleButton toggleRed = FindViewById<ToggleButton>(Resource.Id.toggleButtonRed);
                    InitLed(toggleRed, "red_led/");

                    ToggleButton toggleBlue = FindViewById<ToggleButton>(Resource.Id.toggleButtonBlue);
                    InitLed(toggleBlue, "blue_led/");

                    Button buttonMeasure = FindViewById<Button>(Resource.Id.buttonMeasure);
                    buttonMeasure.Click += async (sender, e) =>
                    {
                        await FetchApiTempAsync();
                    };

                    Button buttonAdc = FindViewById<Button>(Resource.Id.buttonAdc);
                    buttonAdc.Click += async (sender, e) =>
                    {
                        await FetchApiAdcAsync();
                    };
                };
                */
            }
            catch (Exception ex)
            {
                exceptionBox.Text = ex.ToString();
            }

            layout.AddView(exceptionBox);
            SetContentView(layout);
        }

        /*
        private async void InitLed(ToggleButton toggle, string uriPart, TextView exceptionBox)
        {
            AutoCompleteTextView baseUri = FindViewById<AutoCompleteTextView>(Resource.Id.autoCompleteTextViewWebserviceBaseUri);

            toggle.Click += async (sender, e) =>
            {
                if (((ToggleButton)sender).Checked)
                {
                    JsonValue json1 = await FetchApiAsync(baseUri.Text + uriPart + "on", exceptionBox);
                }
                else
                {
                    JsonValue json1 = await FetchApiAsync(baseUri.Text + uriPart + "off", exceptionBox);
                }
            };

            JsonValue json = await FetchApiAsync(baseUri.Text + uriPart + "state", exceptionBox);
            toggle.Checked = json["value"].ToString().Equals("1");
        }*/

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

        /*
        private async Task<bool> FetchApiTempAsync(TextView exceptionBox)
        {
            AutoCompleteTextView baseUri = FindViewById<AutoCompleteTextView>(Resource.Id.autoCompleteTextViewWebserviceBaseUri);
            TextView textViewTemperature = FindViewById<TextView>(Resource.Id.textViewTemperature);
            TextView textViewHumidity = FindViewById<TextView>(Resource.Id.textViewHumidity);

            JsonValue measure = await FetchApiAsync(baseUri.Text + "dht11/measure", exceptionBox);

            JsonValue temperature = await FetchApiAsync(baseUri.Text + "dht11/temperature", exceptionBox);
            textViewTemperature.Text = "Temperature: " + temperature["value"];

            JsonValue humidity = await FetchApiAsync(baseUri.Text + "dht11/humidity", exceptionBox);
            textViewHumidity.Text = "Humidity: " + humidity["value"];

            return true;
        }

        private async Task<bool> FetchApiAdcAsync(TextView exceptionBox)
        {
            AutoCompleteTextView baseUri = FindViewById<AutoCompleteTextView>(Resource.Id.autoCompleteTextViewWebserviceBaseUri);
            TextView textViewAdc = FindViewById<TextView>(Resource.Id.textViewAdc);

            JsonValue adcValue = await FetchApiAsync(baseUri.Text + "hygrometer/read", exceptionBox);
            textViewAdc.Text = "Value: " + adcValue["value"].ToString();

            return true;
        }
        */

        private async Task<bool> FetchApiLayout(string baseUri, LinearLayout layout, TextView exceptionBox)
        {
            try
            {
                JsonValue value = await FetchApiAsync(baseUri + "?class", exceptionBox);
                foreach (KeyValuePair<string, JsonValue> kvp in value)
                {
                    string cls = kvp.Value["class"];
                    string uri = baseUri + "/" + kvp.Key + "/";
                    if (cls.Equals("Led"))
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
                    else if (cls.Equals("Dht11"))
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
                                JsonValue measure = await FetchApiAsync(uri + "measure", exceptionBox);
                            }
                            catch (Exception ex)
                            {
                                exceptionBox.Text = ex.ToString();
                            }

                            JsonValue temperature = await FetchApiAsync(uri + "temperature", exceptionBox);
                            textViewTemperature.Text = "Temperature: " + temperature["value"];

                            JsonValue humidity = await FetchApiAsync(uri + "humidity", exceptionBox);
                            textViewHumidity.Text = "Humidity: " + humidity["value"];
                        };
                        layout.AddView(buttonMeasure);
                        layout.AddView(textViewTemperature);
                        layout.AddView(textViewHumidity);
                    }
                    else if (cls.Equals("Adc"))
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

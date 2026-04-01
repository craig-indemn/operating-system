using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.ServiceModel;
using System.ServiceModel.Channels;
using System.Xml;

[ServiceContract(Namespace = "http://tempuri.org/")]
interface IIMSService
{
    [OperationContract(Action = "http://tempuri.org/IIMSService/GetToken",
                       ReplyAction = "http://tempuri.org/IIMSService/GetTokenResponse")]
    Message GetToken(Message request);

    // Generic catch-all — any operation via Message contract
    [OperationContract(Action = "*", ReplyAction = "*")]
    Message ProcessMessage(Message request);
}

class UniExplore
{
    static string accessToken;
    static StreamWriter logWriter;

    static void Main(string[] args)
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        ServicePointManager.ServerCertificateValidationCallback =
            delegate(object s, X509Certificate cert, X509Chain chain, SslPolicyErrors errors) { return true; };

        string outFile = args.Length > 0 ? args[0] : "C:\\unisoft\\explore-results.txt";

        using (logWriter = new StreamWriter(outFile))
        {
            Log("=== Unisoft API Exploration ===");
            Log("Time: " + DateTime.UtcNow.ToString("o"));
            Log("");

            try
            {
                var binding = new WSHttpBinding();
                binding.Security.Mode = SecurityMode.TransportWithMessageCredential;
                binding.Security.Message.ClientCredentialType = MessageCredentialType.UserName;
                binding.Security.Message.EstablishSecurityContext = true;
                binding.ReliableSession.Enabled = true;
                binding.MaxReceivedMessageSize = 50 * 1024 * 1024;
                binding.ReaderQuotas.MaxStringContentLength = 50 * 1024 * 1024;
                binding.ReaderQuotas.MaxArrayLength = 50 * 1024 * 1024;
                binding.OpenTimeout = TimeSpan.FromSeconds(30);
                binding.SendTimeout = TimeSpan.FromSeconds(120);
                binding.ReceiveTimeout = TimeSpan.FromSeconds(120);

                var endpoint = new EndpointAddress(
                    "https://services.uat.gicunderwriters.co/management/imsservice.svc");
                var factory = new ChannelFactory<IIMSService>(binding, endpoint);
                factory.Credentials.UserName.UserName = "UniClient";
                factory.Credentials.UserName.Password = "J5j!}7=r/z";

                Log("Opening channel...");
                var channel = factory.CreateChannel();
                ((IClientChannel)channel).Open();
                Log("Channel open.\n");

                // 1. GetToken
                Log("========== 1. GetToken ==========");
                string tokenXml = CallOp(channel, "GetToken", @"
                    <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                        <AccessToken i:nil=""true"" xmlns=""""/>
                        <ClientId xmlns="""">GIC_UAT</ClientId>
                        <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                        <IsDeveloper xmlns="""">false</IsDeveloper>
                        <RequestId xmlns="""">00000000-0000-0000-0000-000000000001</RequestId>
                        <RequestedByUserName i:nil=""true"" xmlns=""""/>
                        <Version i:nil=""true"" xmlns=""""/>
                    </request>");
                accessToken = ExtractValue(tokenXml, "AccessToken");
                Log("Token: " + accessToken + "\n");

                // 2. GetInsuranceLOBs
                Log("========== 2. GetInsuranceLOBs ==========");
                CallAndLog(channel, "GetInsuranceLOBs", StandardRequest());

                // 3. GetLOBs (different operation — may have more)
                Log("========== 3. GetLOBs ==========");
                CallAndLog(channel, "GetLOBs", StandardRequest());

                // 4. GetInsuranceSubLOBs for each known LOB
                string[] lobCodes = {"CG", "CV", "CP", "CU", "EX", "FL", "GA", "HO", "IM", "IP", "ML", "OM", "PI", "PU", "PA", "PL", "TR", "WC"};
                foreach (string lob in lobCodes)
                {
                    Log("========== 4. GetInsuranceSubLOBs (LOB=" + lob + ") ==========");
                    CallAndLog(channel, "GetInsuranceSubLOBs", StandardRequest("<LOB xmlns=\"\">" + lob + "</LOB>"));
                }

                // 5. GetInsuranceCarriers
                Log("========== 5. GetInsuranceCarriers ==========");
                CallAndLog(channel, "GetInsuranceCarriers", StandardRequest());

                // 6. GetCarriersForLookup
                Log("========== 6. GetCarriersForLookup ==========");
                CallAndLog(channel, "GetCarriersForLookup", StandardRequest());

                // 7. GetAgentsAndProspectsForLookup
                Log("========== 7. GetAgentsAndProspectsForLookup ==========");
                CallAndLog(channel, "GetAgentsAndProspectsForLookup", StandardRequest());

                // 8. GetQuote (known test quote 17129)
                Log("========== 8. GetQuote (17129) ==========");
                CallAndLog(channel, "GetQuote", @"
                    <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                        <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                        <ClientId xmlns="""">GIC_UAT</ClientId>
                        <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                        <IsDeveloper xmlns="""">false</IsDeveloper>
                        <RequestId xmlns="""">" + Guid.NewGuid() + @"</RequestId>
                        <RequestedByUserName i:nil=""true"" xmlns=""""/>
                        <Version i:nil=""true"" xmlns=""""/>
                        <QuoteId xmlns="""">17129</QuoteId>
                    </request>");

                // 9. GetSubmissions (for quote 17129)
                Log("========== 9. GetSubmissions (QuoteId=17129) ==========");
                CallAndLog(channel, "GetSubmissions", @"
                    <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                        <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                        <ClientId xmlns="""">GIC_UAT</ClientId>
                        <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                        <IsDeveloper xmlns="""">false</IsDeveloper>
                        <RequestId xmlns="""">" + Guid.NewGuid() + @"</RequestId>
                        <RequestedByUserName i:nil=""true"" xmlns=""""/>
                        <Version i:nil=""true"" xmlns=""""/>
                        <QuoteId xmlns="""">17129</QuoteId>
                    </request>");

                // 10. GetQuoteActions (activity types)
                Log("========== 10. GetQuoteActions ==========");
                CallAndLog(channel, "GetQuoteActions", StandardRequest());

                // 11. GetSections (UI sections)
                Log("========== 11. GetSections ==========");
                CallAndLog(channel, "GetSections", StandardRequest());

                // 12. GetCompanyRules
                Log("========== 12. GetCompanyRules ==========");
                CallAndLog(channel, "GetCompanyRules", StandardRequest());

                // 13. GetBrokersForLookup
                Log("========== 13. GetBrokersForLookup ==========");
                CallAndLog(channel, "GetBrokersForLookup", StandardRequest());

                // 14. GetActivitiesByQuoteId (for quote 17129)
                Log("========== 14. GetActivitiesByQuoteId (17129) ==========");
                CallAndLog(channel, "GetActivitiesByQuoteId", @"
                    <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                        <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                        <ClientId xmlns="""">GIC_UAT</ClientId>
                        <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                        <IsDeveloper xmlns="""">false</IsDeveloper>
                        <RequestId xmlns="""">" + Guid.NewGuid() + @"</RequestId>
                        <RequestedByUserName i:nil=""true"" xmlns=""""/>
                        <Version i:nil=""true"" xmlns=""""/>
                        <QuoteId xmlns="""">17129</QuoteId>
                    </request>");

                ((IClientChannel)channel).Close();
                factory.Close();
                Log("\n=== ALL DONE ===");
            }
            catch (Exception ex)
            {
                Log("FATAL: " + ex.GetType().Name + ": " + ex.Message);
                if (ex.InnerException != null)
                    Log("Inner: " + ex.InnerException.Message);
                Log(ex.StackTrace);
            }
        }

        Console.WriteLine("Results written to: " + outFile);
        Console.WriteLine("File size: " + new FileInfo(outFile).Length + " bytes");
    }

    static string StandardRequest(string extraFields = "")
    {
        return @"
            <request xmlns:i=""http://www.w3.org/2001/XMLSchema-instance"">
                <AccessToken xmlns="""">" + accessToken + @"</AccessToken>
                <ClientId xmlns="""">GIC_UAT</ClientId>
                <CompanyInitials xmlns="""">GIC_UAT</CompanyInitials>
                <IsDeveloper xmlns="""">false</IsDeveloper>
                <RequestId xmlns="""">" + Guid.NewGuid() + @"</RequestId>
                <RequestedByUserName i:nil=""true"" xmlns=""""/>
                <Version i:nil=""true"" xmlns=""""/>
                " + extraFields + @"
            </request>";
    }

    static string CallOp(IIMSService channel, string opName, string requestInner)
    {
        string bodyXml = "<" + opName + " xmlns=\"http://tempuri.org/\">" + requestInner + "</" + opName + ">";
        var reader = XmlReader.Create(new StringReader(bodyXml));
        var msg = Message.CreateMessage(
            MessageVersion.Soap12WSAddressing10,
            "http://tempuri.org/IIMSService/" + opName,
            reader);

        Message result;
        try
        {
            result = channel.ProcessMessage(msg);
        }
        catch (Exception ex)
        {
            return "CALL_ERROR: " + ex.Message;
        }

        return MsgToString(result);
    }

    static void CallAndLog(IIMSService channel, string opName, string requestInner)
    {
        try
        {
            string result = CallOp(channel, opName, requestInner);
            Log(result);
            // Extract status
            string status = ExtractValue(result, "ReplyStatus");
            if (status != null) Log("[Status: " + status + "]");
        }
        catch (Exception ex)
        {
            Log("ERROR: " + ex.Message);
        }
        Log("");
    }

    static string ExtractValue(string xml, string tag)
    {
        try
        {
            string openTag = "<" + tag;
            int start = xml.IndexOf(openTag);
            if (start < 0) return null;
            // Check for nil
            int tagEnd = xml.IndexOf(">", start);
            string tagStr = xml.Substring(start, tagEnd - start + 1);
            if (tagStr.Contains("nil=\"true\"")) return null;
            start = tagEnd + 1;
            int end = xml.IndexOf("</" + tag + ">", start);
            if (end < 0) return null;
            return xml.Substring(start, end - start);
        }
        catch { return null; }
    }

    static string MsgToString(Message msg)
    {
        using (var sw = new StringWriter())
        using (var writer = XmlWriter.Create(sw, new XmlWriterSettings { Indent = true }))
        {
            msg.WriteBody(writer);
            writer.Flush();
            return sw.ToString();
        }
    }

    static void Log(string text)
    {
        Console.WriteLine(text);
        logWriter.WriteLine(text);
        logWriter.Flush();
    }
}

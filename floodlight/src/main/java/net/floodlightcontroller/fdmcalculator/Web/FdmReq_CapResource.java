package net.floodlightcontroller.fdmcalculator.Web;




import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;
import java.util.List;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

import org.projectfloodlight.openflow.types.DatapathId;
import org.projectfloodlight.openflow.types.OFPort;
import org.projectfloodlight.openflow.types.U64;
import org.restlet.resource.Get;
import org.restlet.resource.Post;
import org.restlet.resource.ServerResource;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.MappingJsonFactory;

import net.floodlightcontroller.fdmcalculator.CustomizedLink;
import net.floodlightcontroller.fdmcalculator.IFDMCalculatorService;
//import net.floodlightcontroller.linkdiscovery.web.LinkWithType;
import net.floodlightcontroller.linkdiscovery.ILinkDiscoveryService;
import net.floodlightcontroller.linkdiscovery.Link;
import net.floodlightcontroller.linkdiscovery.ILinkDiscovery.LinkDirection;
import net.floodlightcontroller.linkdiscovery.ILinkDiscovery.LinkType;
import net.floodlightcontroller.linkdiscovery.internal.LinkInfo;
import net.floodlightcontroller.linkdiscovery.web.LinkWithType;


public class FdmReq_CapResource extends ServerResource{
	protected static Logger log = LoggerFactory.getLogger(FdmReq_CapResource.class);
	
	private static final String STR_SRCSW = "src-switch";
	private static final String STR_SRCPOR ="src-port"; 
	private static final String STR_DSTSW = "dst-switch";
	private static final String STR_DSTPOR = "dst-port";
	private static final String STR_CAP = "capacity";
	private static final String STR_REQ = "requirement";
	private static final String STR_CMD = "cmd";
	
	@Get("json")
	public Set<Ruleinfo> retrieveallReq_Cap(){
		IFDMCalculatorService fds = (IFDMCalculatorService)getContext().getAttributes().
                get(IFDMCalculatorService.class.getCanonicalName());
		Set<Ruleinfo> ret = new HashSet<Ruleinfo>();
		Map<String,List<Float>> rulemap = fds.getRules();
		for(String tuple:rulemap.keySet()){
			Ruleinfo rf = new Ruleinfo(tuple,rulemap.get(tuple));
			ret.add(rf);
		}
		
        return ret;
	}
	
	
	@Post
	public String setReq_Cap(String json){
		IFDMCalculatorService fds = (IFDMCalculatorService)getContext().getAttributes().
                get(IFDMCalculatorService.class.getCanonicalName());
		MappingJsonFactory f = new MappingJsonFactory();
		JsonParser jp = null;
		String src_sw = null;
		String src_port = null;
		String dst_sw = null;
		String dst_port = null;
		String cmd = null;
		Float cap = Float.POSITIVE_INFINITY;
		Float req = 0.0f;
		System.out.println(json);
		try{
			try{
				jp = f.createParser(json);
			}
			catch(IOException e){
				e.printStackTrace();
			}
			jp.nextToken();
			if(jp.getCurrentToken() != JsonToken.START_OBJECT){
				throw new IOException("Expected START_OBJECT");
			}
			
			while(jp.nextToken()!=JsonToken.END_OBJECT){ 
				if(jp.getCurrentToken()!=JsonToken.FIELD_NAME){
					throw new IOException("Expected FIELD_NAME");
				}
			
			
				String n = jp.getCurrentName().toLowerCase();
				jp.nextToken();
				switch(n){
				case STR_SRCSW: src_sw = jp.getText();
								break;
				case STR_SRCPOR:src_port = jp.getText();
								break;
				case STR_DSTSW: dst_sw = jp.getText();
								break;
				case STR_DSTPOR:dst_port = jp.getText();
								break;
				case STR_CAP: cap = Float.parseFloat( jp.getText());
								break;
				case STR_REQ: req = Float.parseFloat( jp.getText());
								break;
				case STR_CMD: cmd = jp.getText();
				default : break;
				}
			}
			
		}
    	catch(IOException e){
    		e.printStackTrace();
    		
    	}
		
		if(cmd==null)
		{
			return "Invalid cmd, cmd parameter missing";
		}
		
    	if(src_sw==null||src_port==null||dst_sw==null||dst_port==null){
    		return "Invalid rule, set rules failed\n";
    	}
//    	if(src_sw.equals(dst_sw)){
//    		String rule_key = src_sw+'-'+'0'+'-'+dst_sw+'-'+'0';
//    		if(fds.getRules().containsKey(rule_key)){
//    			if(cmd.equals("DELETE")){
//    				fds.deleterule_path(rule_key);
//    			}
//    			return "Source rule already set in fdm";
//    		}
//    		else{
//    			if(cmd.equals("ADD"))
//    				fds.addRule(rule_key, req, cap);
//    			else if(cmd.equals("DELETE")){
//    				return "Rule was not set before";
//    			}
//    			return "Source rule set successfully";
//    		}
//    	}
//    	else{
    		String rule_key = src_sw+'-'+src_port+'-'+dst_sw+'-'+dst_port;
    		if(fds.getRules().containsKey(rule_key)){
				// if(fds.getRules().get(rule_key).get(0)!= req){
	
				// }
				// if(fds.getRules().get(rule_key).get(1)!= cap){
	
				// }
    			if(cmd.equals("DELETE")){
					fds.deleterule_path(rule_key);
					return "Rule already set in fdm";
				}
    			else if(cmd.equals("MODIFY")){
    				fds.updaterule_path(rule_key, req, cap);
    				return "Rule updated in fdm";
    			}
    			else{
    				return "Rule whatever";
    			}
			}
			else{
				if(cmd.equals("ADD"))
					fds.addRule(rule_key,req,cap);
				else if(cmd.equals("DELETE")){
					return "Rule was not set before";
				}
				return "Rule set successfully";
			}
    	}
		
//	}
}
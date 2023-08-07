<?php
/**
 * IPP23 projekt 1
 * PHP: 8.1
 * Author: Jakub Kurka
 * Date: 6.3.2023
 */

/**
 * chyby:  21 - chybejici hlavicka
 *         22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode23
 *         23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode23
 */
ini_set('display_errors', 'stderr');

$parser = new Parser($argc, $argv);
$parser->parse();
$header = false;
$numLine = 0;


class Parser
{
    public $xml;
    private $argv;
    private $argc;
    public $order;
    public $lineNum;
    private $header;

    /**
    * creates new instance of Parser
    * @param $argc number of arguments
    * @param $argv list of arguments
    */
    public function __construct($argc, $argv)
    {
        $this->argc = $argc;
        $this->argv = $argv;
        $this->header = false;
        $temp = <<<XML
        <?xml version="1.0" encoding="UTF-8" ?>
            <program language="IPPcode23">
            </program>
        XML;

        $this->xml = new SimpleXMLElement($temp);
        $this->order = 1;
        $this->lineNum = 0;
    }

    /**
     * checks every line and instruction. Perform lexical and syntactic analysis of Instruction.
     */
    public function parse()
    {
        $this->checkParams();
        while ($line = fgets(STDIN)) {
            //header check
            if ($this->header == false) {
                if (preg_match('/.(?i)(IPPcode23)/', trim($line))) {
                    $this->header = true;
                }
            } else {
                $comment = explode('#', $line);
                $line = $comment[0];
                if (strlen(trim($line)) == 0)
                {
                    continue; //pokud je radek prazdnej, nebo komentar
                }
                $ins = new Instruction($line, $this->order);
                if (!$ins->checkName())
                    exit(22); //chybny kod
                $ins->create_XML_element($this->xml);
                $this->order++;
            }
        }
        if($this->header == false)
        {
            echo("end\n");
            exit(21);
        }
        echo $this->xml->asXML();
    }

    //checks parameters of the program
    private function checkParams()
    {
        if ($this->argc == 2 && $this->argv[1] == '--help') {
            if($this->argc > 2)
            {
                echo("K argumentu --help není možno přidat další argument.\n");
                exit(10);
            }
            $this->printHelp();
        }
        
    }

    //prints helpful information
    private function printHelp()
    {
        echo "Usage: php8.1 parse.php < STDIN > STDOUT\n"
            . "Optional parameters:\n"
            . "\t[--help] - to print this message\n"
            . "\nAuthor: Jakub Kurka\n"
            . "Login: xkurka06\n"
            . "Date: 1.3.2023\n";
        exit(0);
    }
}

/**
 * @param $line String with instruction
 * @param $numLine number of instruction
 */
class Instruction
{
    public $name = ""; //jmeno instrukce
    public $args = []; //argumenty instrukce
    public $numLine = 0; //poradi instrukce
    private $validNames = "";

    public function __construct($line, $numLine)
    {
        $splitted = explode(' ', trim($line, "\n"));

        $this->name = strtoupper($splitted[0]);
        $this->args = $this->get_arguments($splitted);
        $this->numLine = $numLine;
        //FUNNY VALIDNI JMENA IWKMS
        $this->validNames = [
            "MOVE",
            "CREATEFRAME",
            "PUSHFRAME",
            "POPFRAME",
            "DEFVAR",
            "CALL",
            "RETURN",
            "PUSHS",
            "POPS",
            "CLEARS",
            "ADD",
            "SUB",
            "MUL",
            "DIV",
            "IDIV",
            "ADDS",
            "SUBS",
            "MULS",
            "DIVS",
            "IDIVS",
            "LT",
            "GT",
            "EQ",
            "LTS",
            "GTS",
            "EQS",
            "AND",
            "OR",
            "NOT",
            "ANDS",
            "ORS",
            "NOTS",
            "INT2FLOAT",
            "FLOAT2INT",
            "INT2CHAR",
            "STRI2INT",
            "INT2FLOATS",
            "FLOATS2INTS",
            "INT2CHARS",
            "STRI2INTS",
            "READ",
            "WRITE",
            "CONCAT",
            "STRLEN",
            "GETCHAR",
            "SETCHAR",
            "TYPE",
            "LABEL",
            "JUMP",
            "JUMPIFEQ",
            "JUMPIFNEQ",
            "JUMPIFEQS",
            "JUMPIFNEQS",
            "EXIT",
            "BREAK",
            "DPRINT",
        ];
    }

    //gets arguments from line
    private function get_arguments($splitted)
    {
        $list = [];
        for ($i = 1; $i < count($splitted); $i++) {
            if(strlen(trim($splitted[$i])) != 0)
            {
                array_push($list, $splitted[$i]);
            }
        }
        return $list;
    }

    //create element from instruction with children
    public function create_XML_element(SimpleXMLElement $xml)
    {
        if (!($this->checkName())) //kontrola jestli je validni instrukce
        {
            exit(22);
        }
        $element = $xml->addChild("instruction");
        $element->addAttribute("order", $this->numLine);
        $element->addAttribute("opcode", $this->name);

        //odstranit komentare a MEZERY z arraye
        foreach ($this->args as $key => $value) {
            if (strlen(trim($value)) == 0) {
                array_splice($this->args, $key, 1);
            }
        }
        switch ($this->name) {
            // <var>
            case 'DEFVAR':
            case 'POPS':
                if (count($this->args) == 1) {
                    if ($this->isVar($this->args[0])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'var');
                    } else
                        exit(23);
                } else
                    exit(23);
                break;
            //<no args>
            case 'CREATEFRAME':
            case 'PUSHFRAME':
            case 'POPFRAME':
            case 'RETURN':
            case 'CLEARS':
            case 'BREAK':
                if (count($this->args) != 0) {
                    exit(23);
                } else
                    break;

            //<var> <symb>
            case 'TYPE':
            case 'STRLEN':
            case 'INT2FLOAT':
            case 'FLOAT2INT':
            case 'INT2CHAR':
            case 'INT2FLOATS':
            case 'FLOAT2INTS':
            case 'INT2CHARS':
            case 'MOVE':
                if (count($this->args) == 2) {
                    $isVar = $this->isSymbol($this->args[1]);
                    if ($this->isVar($this->args[0])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'var');
                        if($isVar == 2 || $isVar == 3)
                        {
                            $xd = explode('@', $this->args[1]);
                            $arg = $element->addChild("arg2", htmlspecialchars(trim($xd[1])));
                            $arg->addAttribute('type', $xd[0]);
                        }
                        else if($isVar == 1)
                        {
                            $arg = $element->addChild("arg2", htmlspecialchars(trim($this->args[1])));
                            $arg->addAttribute('type', 'var');
                        }
                        else exit(23);
                    } else
                        {exit(23);}
                } else
                    {exit(23);}
                break;
            //<var> <type>
            case 'READ':
                if (count($this->args) == 2) {
                    if ($this->isVar($this->args[0]) && $this->isType($this->args[1])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'var');
                        $arg = $element->addChild("arg2", htmlspecialchars(trim($this->args[1])));
                        $arg->addAttribute('type', 'type');
                    } else
                        {exit(23);}
                } else
                    {exit(23);}
                break;
            //<label>
            case 'JUMPIFEQS':
            case 'JUMPIFNEQS':
            case 'CALL':
            case 'LABEL':
            case 'JUMP':

                if (count($this->args) == 1) {
                    if ($this->isLabel($this->args[0])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'label');
                    } else
                        {exit(23);}
                } else
                    {exit(23);}
                break;
            //<symb>
            case 'DPRINT':
            case 'EXIT':
            case 'WRITE':
            case 'PUSHS':
                if (count($this->args) == 1) {
                    
                    $isVar = $this->isSymbol($this->args[0]);
                    if ($isVar == 1) //var
                    {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'var');
                    } else if ($isVar == 2 || $isVar == 3) //konstanta a null
                    {
                        $xd = explode('@', $this->args[0]);
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($xd[1])));
                        $arg->addAttribute('type', $xd[0]);
                    } else {
                        exit(23);
                    }
                } else {
                    exit(23);
                }
                break;
            //<var> <symb1> <symb2>
            case 'ADD':
            case 'ADDS':
            case 'SUBS':
            case 'MULS':
            case 'DIVS':
            case 'IDIVS':
            case 'SUB':
            case 'MUL':
            case 'DIV':
            case 'IDIV':
            case 'LT':
            case 'GT':
            case 'EQ':
            case 'LTS':
            case 'GTS':
            case 'EQS':
            case 'AND':
            case 'OR':
            case 'NOT':
            case 'ANDS':
            case 'ORS':
            case 'NOTS':
            case 'CONCAT':
            case 'GETCHAR':
            case 'SETCHAR':
            case 'STRI2INT':
            case 'STRI2INTS':
                if (count($this->args) == 3) {
                    if ($this->isVar($this->args[0])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'var');
                        $isVar = $this->isSymbol($this->args[1]);
                        if($isVar == 1)
                        {
                            $arg = $element->addChild("arg2", htmlspecialchars(trim($this->args[1])));
                            $arg->addAttribute('type', 'var');
                        }
                        else if($isVar == 2 || $isVar == 3){
                            $xd = explode('@', $this->args[1]);
                            $arg = $element->addChild("arg2", htmlspecialchars(trim($xd[1])));
                            $arg->addAttribute('type', $xd[0]);
                        }else exit(23);
                        $isVar = $this->isSymbol($this->args[2]);
                        if($isVar == 1)
                        {
                            $arg = $element->addChild("arg3", htmlspecialchars(trim($this->args[2])));
                            $arg->addAttribute('type', 'var');
                        }
                        else if($isVar == 2 || $isVar == 3){
                            $xd = explode('@', $this->args[2]);
                            $arg = $element->addChild("arg3", htmlspecialchars(trim($xd[1])));
                            $arg->addAttribute('type', $xd[0]);
                        }else {exit(23);}
                    } else
                        {exit(23);}
                } else
                    {exit(23);}
                break;
            // <label> <symb1> <symb2>
            case 'JUMPIFEQ':
            case 'JUMPIFNEQ':
                if (count($this->args) == 3) {
                    if ($this->isLabel($this->args[0])) {
                        $arg = $element->addChild("arg1", htmlspecialchars(trim($this->args[0])));
                        $arg->addAttribute('type', 'label');
                        if ($this->isSymbol($this->args[1]) && $this->isSymbol($this->args[2])) {
                            $xd = explode('@', $this->args[1]);
                            $arg = $element->addChild("arg2", htmlspecialchars(trim($xd[1])));
                            $arg->addAttribute('type', $xd[0]);

                            $xd = explode('@', $this->args[2]);
                            $arg = $element->addChild("arg3", htmlspecialchars(trim($xd[1])));
                            $arg->addAttribute('type', $xd[0]);
                        } else
                            {exit(23);}
                    } else
                        {exit(23);}
                } else
                    {exit(23);}
                break;
        }

    }

    //checks if argument is <Type>
    private function isType($arg)
    {
        if (preg_match("/(int|float|string|bool)/", $arg)) {
            return true;
        } else
            return false;
    }
    //checks if argument is <Var>
    private function isVar($arg)
    {
        if (preg_match("/(LF|GF|TF)@[A-Za-z&*_%!?$-][[A-Za-z&*_%!?$0-9]*/", $arg)) {
            return true;
        } else
            return false;
    }

    //checks if argument is <Symbol>
    private function isSymbol($arg)
    {
        if (preg_match("/(LF|GF|TF)@[A-Za-z&*_%!?$-][A-Za-z&*_%!?$0-9]*/", $arg)) {
            return 1;
        } //je to Var
        else if (preg_match('/^(string@(([^\\\\\s])*([\\\\]([0-9]{3}))*([^\\\\\s])*)*)$|^(int@-?\+?[0-9]+)$|^(bool@(true|false)$|^(nil@nil))$/', $arg)) {
            return 2;
        } //konstanta
        else if (preg_match("/^nil@nil$/", $arg)) {
            return 3; //null
        } else {
            return 0;
        }
    }

    //checks if argument is <Label>
    private function isLabel($arg)
    {
        if (preg_match("/^[\_\-\$\%\*\?\!\&a-zA-Z0-9]+$/", $arg)) {
            return true;
        } else
            return false;
    }

    //pomocna instrukce
    public function print_Instruction()
    {
        $text = "Line $this->numLine: $this->name, ";
        $arg_text = implode(' ', $this->args);
        $text .= "Arguments: " . $arg_text;
        echo ($text . "\n");
    }

    //check if instruction name is valid
    public function checkName()
    {
        return in_array($this->name, $this->validNames);
    }

}
?>
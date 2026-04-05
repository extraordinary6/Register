// ============================================================================
// RegPulse Auto-Generated APB Register Bank
// Module   : chip_regs
// Generated: 2026-04-05 12:38:41
// ============================================================================
module chip_regs (
    // APB Interface
    input  wire        pclk,
    input  wire        presetn,
    input  wire [31:0] paddr,
    input  wire        psel,
    input  wire        penable,
    input  wire        pwrite,
    input  wire [31:0] pwdata,
    output reg  [31:0] prdata,
    output wire        pready,
    // Hardware Interface
    output wire [0:0] ctrl_en_q,
    output wire [3:1] ctrl_mode_q,
    input  wire [0:0] status_done_st,
    input  wire [1:1] status_busy_st,
    input  wire [2:2] status_pend_st,
    output wire [0:0] int_en_done_q,
    output wire [1:1] int_en_timer_q,
    input  wire [0:0] int_sts_overrun_st,
    output wire [0:0] dma_ctrl_start_q,
    output wire [15:8] dma_ctrl_len_q,
    input  wire [0:0] err_sts_parity_st,
    input  wire [1:1] err_sts_crc_err_st
);

    assign pready = 1'b1;

    // ========================================================================
    // Register declarations
    // ========================================================================
    reg [31:0] CTRL; // offset 0x000
    reg [31:0] STATUS; // offset 0x004
    reg [31:0] INT_EN; // offset 0x008
    reg [31:0] INT_STS; // offset 0x00C
    reg [31:0] DMA_CTRL; // offset 0x010
    reg [31:0] ERR_STS; // offset 0x014

    // ========================================================================
    // Hardware output assignments
    // ========================================================================
    assign ctrl_en_q = CTRL[0:0];
    assign ctrl_mode_q = CTRL[3:1];
    assign int_en_done_q = INT_EN[0:0];
    assign int_en_timer_q = INT_EN[1:1];
    assign dma_ctrl_start_q = DMA_CTRL[0:0];
    assign dma_ctrl_len_q = DMA_CTRL[15:8];


    // ========================================================================
    // Reset
    // ========================================================================
    always @(posedge pclk or negedge presetn) begin
        if (!presetn) begin
            CTRL <= 32'h00000000;
            STATUS <= 32'h00000000;
            INT_EN <= 32'h00000000;
            INT_STS <= 32'h00000000;
            DMA_CTRL <= 32'h00000000;
            ERR_STS <= 32'h00000003;
            prdata <= 32'h0;
        end
    end

    // ========================================================================
    // Hardware Input Synchronization
    // ========================================================================
    always @(posedge pclk) begin
        if (presetn) begin
            // STATUS hw input capture
            STATUS[0:0] <= status_done_st;
            STATUS[1:1] <= status_busy_st;
            STATUS[2:2] <= STATUS[2:2] | status_pend_st;
            // INT_STS hw input capture
            INT_STS[0:0] <= INT_STS[0:0] | int_sts_overrun_st;
            // ERR_STS hw input capture
            ERR_STS[0:0] <= ERR_STS[0:0] | err_sts_parity_st;
            ERR_STS[1:1] <= ERR_STS[1:1] | err_sts_crc_err_st;
        end
    end

    // ========================================================================
    // APB Write
    // ========================================================================
    always @(posedge pclk) begin
        if (presetn && psel && penable && pwrite) begin
            case (paddr[4:2])
                0: begin
                    CTRL[0:0] <= pwdata[0:0];
                    CTRL[3:1] <= pwdata[3:1];
                end
                2: begin
                    INT_EN[0:0] <= pwdata[0:0];
                    INT_EN[1:1] <= pwdata[1:1];
                end
                3: begin
                    INT_STS[0:0] <= INT_STS[0:0] & ~pwdata[0:0];
                end
                4: begin
                    DMA_CTRL[15:8] <= pwdata[15:8];
                end
                default: ;
            endcase
        end
    end

    // ========================================================================
    // APB Read (with merged Read-Clear / Read-Set)
    // ========================================================================
    always @(posedge pclk) begin
        if (presetn && psel && penable && !pwrite) begin
            case (paddr[4:2])
                0: prdata <= CTRL;
                1: begin
                    prdata <= STATUS;
                    STATUS[2:2] <= 1'd1;
                end
                2: prdata <= INT_EN;
                3: prdata <= INT_STS;
                4: begin
                    prdata <= DMA_CTRL;
                    DMA_CTRL[0:0] <= 1'd1;
                end
                5: begin
                    prdata <= ERR_STS;
                    ERR_STS[0:0] <= 1'd0;
                    ERR_STS[1:1] <= 1'd0;
                end
                default: prdata <= 32'h0;
            endcase
        end
    end

endmodule